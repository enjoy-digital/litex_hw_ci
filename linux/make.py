#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import sys
import json
import shutil
import argparse
import subprocess
import contextlib

from enum import IntEnum
from datetime import datetime

# Helpers /Constants -------------------------------------------------------------------------------

def copy_file(src, dst):
    try:
        shutil.copyfile(src, dst)
    except Exception as err:
        return 1
    return 0

@contextlib.contextmanager
def switch_dir(path):
    # Save the original working directory.
    original_dir = os.getcwd()
    try:
        # Change to the provided directory.
        os.chdir(path)
        yield
    finally:
        # Restore the orignal directory.
        os.chdir(original_dir)

# Linux Build --------------------------------------------------------------------------------------

buildroot_url = "http://github.com/buildroot/buildroot"
tftp_root     = "/tftpboot"
motd_path     = "buildroot/board/litex/rootfs_overlay/etc/motd"

def linux_clean():
    if os.path.exists("third_party/buildroot"):
        with switch_dir("third_party/buildroot"):
           return subprocess.run(["make", "clean"]).returncode
    return 0

def linux_generate_motd(cpu_type):
    linux_on_litex_ascii_art = """
   __   _                                  __   _ __      _  __
  / /  (_)__  __ ____ _________  ___  ____/ /  (_) /____ | |/_/
 / /__/ / _ \\/ // /\\ \\ /___/ _ \\/ _ \\/___/ /__/ / __/ -_)>  <
/____/_/_//_/\\_,_//_\\_\\    \\___/_//_/   /____/_/\\__/\\__/_/|_|

"""
    # Create Motd Content.
    motd_content = []
    motd_content.append(linux_on_litex_ascii_art)
    motd_content.append(f"CPU Type   : {cpu_type}")
    motd_content.append(f"Build Date : {datetime.now().strftime('%Y-%m-%d')}")
    motd_content.append("")
    motd_content = "\n".join(motd_content)

    # Write Motd Content to file.
    os.makedirs(os.path.dirname(motd_path), exist_ok=True)
    with open(motd_path, "w") as motd_file:
        motd_file.write(motd_content)

def linux_build(cpu_type):
    # Create Third-Party directory (if not present) and switch to it.
    os.makedirs("third_party", exist_ok=True)
    with switch_dir("third_party"):
        # Get Buildroot.
        if not os.path.exists("buildroot"):
            ret = os.system(f"git clone --depth 1 --single-branch -b master {buildroot_url}")
            if ret != 0:
                return ret

        # Switch to Buildroot directory.
        with switch_dir("buildroot"):
            # Prepare env (LD_LIBRARY_PATH is forbidden).
            env = os.environ
            if "LD_LIBRARY_PATH" in env:
                env.pop("LD_LIBRARY_PATH")

            # Configure Buildroot.
            ret = subprocess.run(f"make BR2_EXTERNAL=../../buildroot/ litex_{cpu_type}_defconfig", shell=True, env=env)
            if ret.returncode != 0:
                return ret

            # Run Buildroot to generate Linux Images.
            ret = subprocess.run("make", shell=True, env=env)

            return ret.returncode

def linux_prepare_tftp(tftp_root=tftp_root, rootfs="ram0", cpu_type=""):
    extra_name = {True: "rocket_", False: ""}[cpu_type == "rocket"]
    ret  = os.system(f"cp images/* {tftp_root}/")
    ret |= os.system(f"cp images/boot_{extra_name}rootfs_{rootfs}.json {tftp_root}/boot.json")
    return ret

def linux_copy_images(soc_json):
    base_dir   = os.path.dirname(soc_json)
    images_dir = os.path.join(base_dir, "images")

    # Create images directory.
    os.makedirs(images_dir, exist_ok=True)

    # Path to boot.json within the images directory
    boot_json_path = os.path.join("images", "boot.json")

    # Copy boot.json to images directory.
    try:
        shutil.copyfile(boot_json_path, os.path.join(images_dir, "boot.json"))
    except Exception as err:
        return 1

    # Copy files listed in boot.json to images directory.
    try:
        with open(boot_json_path, 'r') as json_file:
            json_content = json.load(json_file)
            for filename in json_content.keys():
                src_path = os.path.join("images", filename)
                dst_path = os.path.join(images_dir, filename)
                try:
                    shutil.copyfile(src_path, dst_path)
                except Exception as err:
                    return 1
    except Exception as err:
        return 1

    return 0

# Device Tree --------------------------------------------------------------------------------------

from litex.tools.litex_json2dts_linux import generate_dts as litex_generate_dts

# DTS generation.
# ---------------

def generate_dts(soc_json, rootfs="ram0", cpu_type=""):
    base_dir = os.path.dirname(soc_json)
    dts = os.path.join(base_dir, "soc.dts")
    initrd = "enabled" if rootfs == "ram0" else "disabled"
    if cpu_type.startswith("naxriscv"):
        cpu_type = "naxriscv"
    if rootfs == "ram0" and cpu_type == "rocket":
        initrd_start = 0x02000000
        initrd_size  = 0x01000000
    else:
        initrd_start = None
        initrd_size  = None
    with open(soc_json) as json_file, open(dts, "w") as dts_file:
        dts_content = litex_generate_dts(json.load(json_file),
            initrd_start = initrd_start,
            initrd_size  = initrd_size,
            initrd       = initrd,
            polling      = False,
            root_device  = rootfs
        )
        dts_file.write(dts_content)



# DTS compilation.
# ----------------

def compile_dts(soc_json, symbols=False):
    base_dir = os.path.dirname(soc_json)
    dts      = os.path.join(base_dir, "soc.dts")
    dtb      = os.path.join(base_dir, "soc.dtb")
    try:
        subprocess.check_call(f"dtc {'-@' if symbols else ''} -O dtb -o {dtb} {dts}", shell=True)
    except subprocess.CalledProcessError as err:
        return err.returncode
    return 0

# DTB combination.
# ----------------

def combine_dtb(soc_json, overlays=""):
    base_dir = os.path.dirname(soc_json)
    dtb_in   = os.path.join(base_dir, "soc.dtb")
    dtb_out  = os.path.join(base_dir, "soc_combined.dtb")
    if overlays == "":
        ret = copy_file(dtb_in, dtb_out)
    else:
        try:
            ret = subprocess.check_call(f"fdtoverlay -i {dtb_in} -o {dtb_out} {overlays}", shell=True)
        except subprocess.CalledProcessError as err:
            ret = err.returncode
    return ret

# DTB copy.
# ---------

def copy_dtb(soc_json):
    base_dir = os.path.dirname(soc_json)
    dtb_in   = os.path.join(base_dir, "soc.dtb")
    dtb_out  = os.path.join("images", "soc.dtb")
    ret = copy_file(dtb_in, dtb_out)
    if ret != 0:
        return ret
    dtb_in   = os.path.join(base_dir, "soc_combined.dtb")
    dtb_out  = os.path.join("images", "soc_combined.dtb")
    return copy_file(dtb_in, dtb_out)

# Main ---------------------------------------------------------------------------------------------

def main():
    print("""
                                    __   _ __      _  __
                                   / /  (_) /____ | |/_/
                                  / /__/ / __/ -_)>  <
                                 /____/_/\\__/\\__/_/|_|
                              LiteX Hardware CI/Linux Tests.

                      Copyright 2024 / Enjoy-Digital <enjoy-digital.fr>
""")
    description = "LiteX Hardware CI/Linux Tests.\n\n"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

    # SoC Arguments.
    # --------------
    parser.add_argument("soc_json",                                  help="SoC JSON file.")

    # RootFS Arguments.
    # -----------------
    parser.add_argument("--rootfs",             default="ram0",      help="Location of the RootFS: ram0 or mmcblk0p2")

    # Build Arguments.
    # ----------------
    parser.add_argument("--clean",        action="store_true", help="Clean Linux Build.")
    parser.add_argument("--build",        action="store_true", help="Build Linux Images (through Buildroot) and Device Tree.")
    parser.add_argument("--generate-dtb", action="store_true", help="Prepare Linux Device Tree.")
    parser.add_argument("--prepare-tftp", action="store_true", help="Prepare/Copy Linux Images to TFTP root directory.")
    parser.add_argument("--copy-images",  action="store_true", help="Copy Linux Images to target build directory.")

    args = parser.parse_args()

    # ErrorsCode.
    # -----------
    class ErrorCode(IntEnum):
        SUCCESS            = 0
        CONFIG_ERROR       = 1
        CLEAN_ERROR        = 2
        DTS_ERRROR         = 3
        BUILD_ERROR        = 4
        TFTP_ERROR         = 5
        COPY_ERROR         = 6

    # Extract information from json file.
    # -----------------------------------
    with open(args.soc_json) as json_file:
        json_content = json.load(json_file)
        cpu_type = json_content["constants"]["config_cpu_human_name"]
        if cpu_type.startswith("vexriscv"):
            cpu_type = "vexriscv"
        elif cpu_type.startswith("naxriscv 32-bit"):
            cpu_type = "naxriscv_32"
        elif cpu_type.startswith("naxriscv 64-bit"):
            cpu_type = "naxriscv_64"
        elif cpu_type.startswith("rocket"):
            cpu_type = "rocket"
        else:
            print(f"Error: unknown cpu_type {cpu_type}")
            return ErrorCode.CONFIG_ERROR

    # Linux Clean.
    # ------------
    if args.clean:
        if linux_clean() != 0:
            return ErrorCode.CLEAN_ERROR

    # Linux Device Tree Generation.
    # -----------------------------
    if args.generate_dtb:
        generate_dts(args.soc_json, rootfs=args.rootfs, cpu_type=cpu_type)
        if compile_dts(args.soc_json) != 0:
            return ErrorCode.DTS_ERROR
        if combine_dtb(args.soc_json) != 0:
            return ErrorCode.DTS_ERROR
        if copy_dtb(args.soc_json) != 0:
            return ErrorCode.DTS_ERROR

    #  Linux Build.
    # -------------
    if args.build:
        extra_name = {True: "rocket_", False: ""}[cpu_type == "rocket"] # FIXME: Avoid/Remove.
        if copy_file(f"images/boot_{extra_name}rootfs_{args.rootfs}.json", "images/boot.json") != 0:
            return ErrorCode.BUILD_ERROR
        linux_generate_motd(cpu_type)
        if linux_build(cpu_type) != 0:
            return ErrorCode.BUILD_ERROR

    # TFTP-Prepare.
    # -------------
    if args.prepare_tftp:
        if linux_prepare_tftp(rootfs=args.rootfs, cpu_type=cpu_type) != 0:
            return ErrorCode.TFTP_ERROR

    # Images Copy.
    # ------------
    if args.copy_images:
        if linux_copy_images(soc_json=args.soc_json) != 0:
            return ErrorCode.COPY_ERROR

    return ErrorCode.SUCCESS

if __name__ == "__main__":
    sys.exit(main())
