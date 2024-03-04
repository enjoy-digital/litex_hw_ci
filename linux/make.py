#!/usr/bin/env python3

import os
import sys
import json
import argparse
import shutil
import subprocess

# Helpers ------------------------------------------------------------------------------------------

def create_third_party_dir():
    if not os.path.exists("third_party"):
        os.makedirs("third_party")

def copy_file(src, dst):
    try:
        shutil.copyfile(src, dst)
    except shutil.SameFileError as err:
        return 1
    except IOError as err:
        return 1
    return 0


# Linux Build --------------------------------------------------------------------------------------

def linux_clean():
    ret = 0
    if os.path.exists("third_party/buildroot"):
        os.chdir("third_party/buildroot")
        ret = os.system("make clean")
        os.chdir("../../")
    return ret

def linux_build(cpu_type, xlen=32, with_usb=False):
    # naxriscv may be configured in 32 or 64bits mode
    if cpu_type == "naxriscv":
        cpu_type = f"{cpu_type}_{xlen}"
    elif with_usb:
        cpu_type = f"{cpu_type}_usbhost"

    # Be sure third_party dir is present and switch to it.
    create_third_party_dir()
    os.chdir("third_party")

    # Get Buildroot.
    if not os.path.exists("buildroot"):
        ret = os.system("git clone --depth 1 --single-branch -b master http://github.com/buildroot/buildroot")
        if ret != 0:
            return ret
    os.chdir("buildroot")

    # Prepare env (LD_LIBRARY_PATH is forbidden)
    env = os.environ
    if "LD_LIBRARY_PATH" in env:
        env.pop("LD_LIBRARY_PATH")

    # Configure Buildroot.
    ret = subprocess.run(f"make BR2_EXTERNAL=../../buildroot/ litex_{cpu_type}_defconfig", shell=True, env=env)
    if ret.returncode != 0:
        return ret

    # Build Linux Images.
    ret = subprocess.run("make", shell=True, env=env)

    # Go back to repo root directory.
    os.chdir("../../")
    return ret.returncode

def linux_prepare_tftp(tftp_root="/tftpboot", rootfs="ram0"):
    ret = os.system(f"cp images/* /tftpboot/")
    ret |= os.system(f"cp images/boot_rootfs_{rootfs}.json /tftpboot/boot.json")
    return ret

def linux_copy_images(soc_json):
    base_dir   = os.path.dirname(soc_json)
    images_dir = os.path.join(base_dir, "images")

    # Create target directory
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    # extracts files to copy from boot.json and copy it
    with open(os.path.join("images", "boot.json")) as json_file:
        json_content = json.load(json_file)
        ret = copy_file("images/boot.json", f"{images_dir}/{boot.json}")
        if ret != 0:
            return ret
        for f in json_content.keys():
            ret = copy_file(f"images/{f}", "{images_dir}/{f}")
            if ret != 0:
                return ret
    return 0

# Device Tree --------------------------------------------------------------------------------------

from litex.tools.litex_json2dts_linux import generate_dts as litex_generate_dts

# DTS generation ---------------------------------------------------------------------------

def generate_dts(soc_json, rootfs="ram0"):
    base_dir = os.path.dirname(soc_json)
    dts = os.path.join(base_dir, "soc.dts")
    initrd = "enabled" if rootfs == "ram0" else "disabled"
    with open(soc_json) as json_file, open(dts, "w") as dts_file:
        dts_content = litex_generate_dts(json.load(json_file), initrd=initrd, polling=False, root_device=rootfs)
        dts_file.write(dts_content)



# DTS compilation --------------------------------------------------------------------------

def compile_dts(soc_json, symbols=False):
    base_dir = os.path.dirname(soc_json)
    dts      = os.path.join(base_dir, "soc.dts")
    dtb      = os.path.join(base_dir, "soc.dtb")
    try:
        subprocess.check_call(f"dtc {'-@' if symbols else ''} -O dtb -o {dtb} {dts}", shell=True)
    except subprocess.CalledProcessError as err:
        return err.returncode
    return 0

# DTB combination --------------------------------------------------------------------------

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

# DTB copy ---------------------------------------------------------------------------------

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

                      Copyright 2024 / Enjoy-Digital and LiteX developers.
""")
    description = "LiteX Hardware CI Tests.\n\n"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

    # SoC/Board.
    parser.add_argument("--soc-json",                                      help="SoC JSON file.")
    # RootFS.
    parser.add_argument("--rootfs",               default="ram0",          help="Location of the RootFS: ram0 or mmcblk0p2")

    # Linux.
    parser.add_argument("--linux-clean",          action="store_true",     help="Clean Linux Build.")
    parser.add_argument("--linux-build",          action="store_true",     help="Build Linux Images (through Buildroot) and Device Tree.")
    parser.add_argument("--linux-generate-dtb",   action="store_true",     help="Prepare device tree.")
    parser.add_argument("--linux-prepare-tftp",   action="store_true",     help="Prepare/Copy Linux Images to TFTP root directory.")
    parser.add_argument("--linux-copy-images",    action="store_true",     help="Copy Linux Images to target build directory.")

    args = parser.parse_args()

    assert args.soc_json is not None

    # Extract information from json file.
    # -----------------------------------
    with open(args.soc_json) as json_file:
        json_content = json.load(json_file)
        with_usb  = "usb_ohci_ctrl" in json_content["memories"]
        xlen      = {True: 32, False: 64}[json_content["constants"]["config_cpu_isa"].startswith("rv32")]

        cpu_type = json_content["constants"]["config_cpu_human_name"]
        if cpu_type.startswith("vexriscv"):
            cpu_type = "vexriscv"
        elif cpu_type.startswith("naxriscv"):
            cpu_type = "naxriscv"
        elif cpu_type.startswith("rocket"):
            cpu_type = "rocket"
        else:
            print(f"Error: unknown cpu_type {cpu_type}")
            return 1

    # Linux Clean.
    # ------------
    if args.linux_clean:
        if linux_clean() != 0:
            return 1

    # Device Tree Build.
    # ------------------
    if args.linux_generate_dtb:
        generate_dts(args.soc_json, rootfs=args.rootfs)
        if compile_dts(args.soc_json) != 0:
            return 1
        if combine_dtb(args.soc_json) != 0:
            return 1
        if copy_dtb(args.soc_json) != 0:
            return 1

    # Linux Build.
    # ------------
    if args.linux_build:
        if copy_file(f"images/boot_rootfs_{args.rootfs}.json", "images/boot.json") != 0:
            return 1
        if linux_build(cpu_type, xlen=xlen, with_usb=with_usb) != 0:
            return 1

    # TFTP-Prepare.
    # -------------
    if args.linux_prepare_tftp:
        if linux_prepare_tftp(rootfs=args.rootfs) != 0:
            return 1

    # Copy-Images.
    # ------------
    if args.linux_copy_images:
        if linux_copy_images(soc_json=args.soc_json) != 0:
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
