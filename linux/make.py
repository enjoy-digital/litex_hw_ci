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
def generate_dts(board_name, rootfs="ram0"):
    json_src = os.path.join("build", board_name, "soc.json")
    dts = os.path.join("build", board_name, "{}.dts".format(board_name))
    initrd   = "enabled" if rootfs == "ram0" else "disabled"

    with open(json_src) as json_file, open(dts, "w") as dts_file:
        dts_content = litex_generate_dts(json.load(json_file), initrd=initrd, polling=False, root_device=rootfs)
        dts_file.write(dts_content)

# DTS compilation --------------------------------------------------------------------------
def compile_dts(board_name, symbols=False):
    dts = os.path.join("build", board_name, "{}.dts".format(board_name))
    dtb = os.path.join("build", board_name, "{}.dtb".format(board_name))
    subprocess.check_call(
        "dtc {} -O dtb -o {} {}".format("-@" if symbols else "", dtb, dts), shell=True)

# DTB combination --------------------------------------------------------------------------
def combine_dtb(board_name, overlays=""):
    dtb_in = os.path.join("build", board_name, "{}.dtb".format(board_name))
    dtb_out = os.path.join("images", "rv32.dtb")
    if overlays == "":
        shutil.copyfile(dtb_in, dtb_out)
    else:
        subprocess.check_call(
            "fdtoverlay -i {} -o {} {}".format(dtb_in, dtb_out, overlays), shell=True)

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
    parser.add_argument("--board",                default=None,            help="Select Board for build (digilent_arty or ti60).")
    parser.add_argument("--board-variant",        default=None,            help="Select Board variant.")
    parser.add_argument("--cpu-type",             default=None,            help="Select CPU (vexriscv or naxriscv).")
    parser.add_argument("--with-usb",             action="store_true",     help="Enable USB-Host.")
    parser.add_argument("--baudrate",             default=115200,          help="Configure UART Baudrate.")
    parser.add_argument("--local-ip",             default="192.168.1.50",  help="Set Local IP address.")
    parser.add_argument("--remote-ip",            default="192.168.1.100", help="Set Remote IP address of TFTP server.")
    parser.add_argument("--build",                action="store_true",     help="Build SoC on selected board.")
    parser.add_argument("--load",                 action="store_true",     help="Load SoC on selected board.")

    # RootFS.
    parser.add_argument("--rootfs",               default="ram0",          help="Location of the RootFS: ram0 or mmcblk0p2")

    # Linux.
    parser.add_argument("--linux-clean",          action="store_true",     help="Clean Linux Build.")
    parser.add_argument("--linux-build",          action="store_true",     help="Build Linux Images (through Buildroot) and Device Tree.")
    parser.add_argument("--linux-generate-dtb",   action="store_true",     help="Prepare device tree.")
    parser.add_argument("--linux-prepare-tftp",   action="store_true",     help="Prepare/Copy Linux Images to TFTP root directory.")

    # General.
    parser.add_argument("--all",                  action="store_true",     help="Build SoC/Linux and load Board.")

    args = parser.parse_args()

    # SoC/Board Configuration.
    # ------------------------
    if args.cpu_type == "vexriscv":
        cpu_config = f"--cpu-type=vexriscv_smp --cpu-variant=linux "
        cpu_config += "--dcache-width=64 --dcache-size=8192 --dcache-ways=2 --icache-width=64 --icache-size=8192 --icache-ways=2 --dtlb-size=6 --with-coherent-dma"
    elif args.cpu_type == "naxriscv":
        cpu_config = f"--cpu-type=naxriscv"
        cpu_config += f"--scala-args='rvc=true,rvf=true,rvd=true' --with-fpu --with-rvc"
    else:
        print("Error: unknown cpu type")
        return
    soc_config = f"--bus-bursting --uart-baudrate={int(float(args.baudrate))}"

    target = f" -m litex_boards.targets.{args.board}"

    board_cmd  = {
        "digilent_arty": f"{cpu_config} {soc_config} --with-ethernet --eth-ip={args.local_ip} --remote-ip {args.remote_ip} --with-spi-sdcard --sys-clk-freq 100e6",
        "ti60": f"{cpu_config} {soc_config} --with-wishbone-memory --sys-clk-freq=260e6 --with-hyperram --with-sdcard",
    }[args.board]
    if args.board_variant is not None:
        if board == "digilent_arty":
            board_cmd += f" --variant={args.board_variant}"
        else:
            board_cmd += f" --revision={args.board_variant}"
    if args.with_usb:
        board_cmd += " --with-usb"

    # Build-All.
    # ----------
    if args.all:
        args.build              = True
        args.linux_clean        = True
        args.linux_generate_dtb = True
        args.linux_build        = True
        args.linux_prepare_tftp = True
        args.load               = True

    # SoC/Board Build.
    # ----------------
    if args.build:
        print(f"python3 ${target} {board_cmd} --csr-json=build/{args.board}/soc.json --build")
        ret = os.system(f"python3 {target} {board_cmd} --csr-json=build/{args.board}/soc.json --build")
        if ret != 0:
            return

    # Linux Clean.
    # ------------
    if args.linux_clean:
        if linux_clean() != 0:
            return

    # Device Tree Build.
    # ------------------
    if args.linux_generate_dtb:
        generate_dts(args.board, rootfs=args.rootfs)
        compile_dts(args.board)
        combine_dtb(args.board)

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

    # SoC/Board Load.
    # ---------------
    if args.load:
        os.system(f"python3 {target} {board_cmd} --load")

if __name__ == "__main__":
    main()
