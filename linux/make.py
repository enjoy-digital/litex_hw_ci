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
        ret = os.system("git clone http://github.com/buildroot/buildroot")
        if ret != 0:
            return ret
    os.chdir("buildroot")

    # Configure Buildroot.
    ret = os.system(f"make BR2_EXTERNAL=../../buildroot/ litex_{cpu_type}_defconfig")
    if ret != 0:
        return ret

    # Build Linux Images.
    ret = os.system("make")

    # Go back to repo root directory.
    os.chdir("../../")
    return ret

def linux_prepare_tftp(tftp_root="/tftpboot", rootfs="ram0"):
    ret = os.system(f"cp images/* /tftpboot/")
    ret |= os.system(f"cp images/boot_rootfs_{rootfs}.json /tftpboot/boot.json")
    return ret

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
    subprocess.check_call(f"dtc {'-@' if symbols else ''} -O dtb -o {dtb} {dts}", shell=True)

# DTB combination --------------------------------------------------------------------------

def combine_dtb(soc_json, overlays=""):
    base_dir = os.path.dirname(soc_json)
    dtb_in   = os.path.join(base_dir, "soc.dtb")
    dtb_out  = os.path.join(base_dir, "soc_combined.dtb")
    if overlays == "":
        shutil.copyfile(dtb_in, dtb_out)
    else:
        subprocess.check_call(f"fdtoverlay -i {dtb_in} -o {dtb_out} {overlays}", shell=True)

# DTB copy ---------------------------------------------------------------------------------

def copy_dtb(soc_json):
    base_dir = os.path.dirname(soc_json)
    dtb_in   = os.path.join(base_dir, "soc.dtb")
    dtb_out  = os.path.join("images", "soc.dtb")
    shutil.copyfile(dtb_in, dtb_out)
    dtb_in   = os.path.join(base_dir, "soc_combined.dtb")
    dtb_out  = os.path.join("images", "soc_combined.dtb")
    shutil.copyfile(dtb_in, dtb_out)

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
    parser.add_argument("--cpu-type",             default=None,            help="Select CPU (vexriscv or naxriscv).") # FIXME: Remove, can be found in .json.
    parser.add_argument("--with-usb",             action="store_true",     help="Enable USB-Host.")                   # FIXME: Remove, can be found in .json.
    # RootFS.
    parser.add_argument("--rootfs",               default="ram0",          help="Location of the RootFS: ram0 or mmcblk0p2")

    # Linux.
    parser.add_argument("--linux-clean",          action="store_true",     help="Clean Linux Build.")
    parser.add_argument("--linux-build",          action="store_true",     help="Build Linux Images (through Buildroot) and Device Tree.")
    parser.add_argument("--linux-generate-dtb",   action="store_true",     help="Prepare device tree.")
    parser.add_argument("--linux-prepare-tftp",   action="store_true",     help="Prepare/Copy Linux Images to TFTP root directory.")

    args = parser.parse_args()

    # Linux Clean.
    # ------------
    if args.linux_clean:
        if linux_clean() != 0:
            return

    # Device Tree Build.
    # ------------------
    if args.linux_generate_dtb:
        generate_dts(args.soc_json, rootfs=args.rootfs)
        compile_dts(args.soc_json)
        combine_dtb(args.soc_json)
        copy_dtb(args.soc_json)

    # Linux Build.
    # ------------
    if args.linux_build:
        shutil.copyfile(f"images/boot_rootfs_{args.rootfs}.json", "images/boot.json")
        if linux_build(args.cpu_type, with_usb=args.with_usb) != 0:
            return

    # TFTP-Prepare.
    # -------------
    if args.linux_prepare_tftp:
        if linux_prepare_tftp(rootfs=args.rootfs) != 0:
            return

if __name__ == "__main__":
    main()
