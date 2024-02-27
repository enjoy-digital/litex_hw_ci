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

def nuttx_clean():
    ret = 0
    if os.path.exists("third_party/nuttx"):
        os.chdir("third_party/nuttx")
        ret = os.system("make clean")
        os.chdir("../../")
    return ret

def nuttx_build():
    toolchain_name = "xpack-riscv-none-elf-gcc-12.3.0-1"

    # Be sure third_party dir is present and switch to it.
    create_third_party_dir()
    os.chdir("third_party")

    # Get toolchain (debian/ubuntu fails with missing math.h)
    if not os.path.exists(toolchain_name):
        os.system(f"wget https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download/v12.3.0-1/{toolchain_name}-linux-x64.tar.gz")
        os.system(f"tar -xf {toolchain_name}-linux-x64.tar.gz") 
    # Get Nuttx.
    if not os.path.exists("nuttx"):
        ret = os.system("git clone --depth 1 --single-branch https://github.com/apache/nuttx")
        if ret != 0:
            return ret
    # Get Nuttx-apps.
    if not os.path.exists("apps"):
        ret = os.system("git clone --depth 1 --single-branch https://github.com/apache/nuttx-apps apps")
        if ret != 0:
            return ret

    # Pepare environment.
    gcc_path    = os.path.join(os.path.abspath(toolchain_name), "bin")
    env         = os.environ.copy()
    env["PATH"] = f"{gcc_path}" + os.pathsep + env["PATH"]

    os.chdir("nuttx")

    # Configure Nuttx.
    ret = subprocess.run("./tools/configure.sh -E -l arty_a7:netnsh", shell=True, env=env) # FIXME: dynamics target and config
    if ret.returncode != 0:
        return ret

    # Build Nuttx Images.
    ret = subprocess.run("make CC=riscv-none-elf-gcc V=2 -j", shell=True, env=env)

    # Go back to repo root directory.
    os.chdir("../../")
    return ret.returncode

# FIXME: force /tftpboot cleanup ?
def nuttx_prepare_tftp(tftp_root="/tftpboot"):
    # Sanity check.
    for f in ["boot.json", "boot.bin"]:
        if os.path.exists(os.path.join(tftp_root, f)):
            os.remove(os.path.join(tftp_root, f))

    ret = os.system(f"cp third_party/nuttx/nuttx.bin {tftp_root}/boot.bin")
    return ret

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

    # Nuttx.
    parser.add_argument("--nuttx-clean",          action="store_true",     help="Clean Nuttx Build.")
    parser.add_argument("--nuttx-build",          action="store_true",     help="Build Nuttx Images.")
    parser.add_argument("--nuttx-prepare-tftp",   action="store_true",     help="Prepare/Copy Nuttx Images to TFTP root directory.")

    args = parser.parse_args()

    # Nuttx Clean.
    # ------------
    if args.nuttx_clean:
        if nuttx_clean() != 0:
            return

    # Nuttx Build.
    # ------------
    if args.nuttx_build:
        if nuttx_build() != 0:
            return

    # TFTP-Prepare.
    # -------------
    if args.nuttx_prepare_tftp:
        if nuttx_prepare_tftp() != 0:
            return

if __name__ == "__main__":
    main()
