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
# Helpers ------------------------------------------------------------------------------------------

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

# NuttX Build --------------------------------------------------------------------------------------

toolchain_name = "xpack-riscv-none-elf-gcc-12.3.0-1"
gcc_url        = f"https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download/v12.3.0-1/{toolchain_name}-linux-x64.tar.gz"
tftp_root      = "/tftpboot"

def nuttx_clean():
    if os.path.exists("third_party/nuttx"):
        with switch_dir("third_party/nuttx"):
           return subprocess.run(["git", "clean", "-xfd", "."]).returncode
    return 0

def nuttx_build():


    # Create Third-Party directory (if not present) and switch to it.
    os.makedirs("third_party", exist_ok=True)
    with switch_dir("third_party"):
        # Get toolchain (debian/ubuntu fails with missing math.h).
        if not os.path.exists(toolchain_name):
            os.system(f"wget {gcc_url}")
            os.system(f"tar -xf {toolchain_name}-linux-x64.tar.gz")

        # Get NuttX.
        if not os.path.exists("nuttx"):
            ret = os.system("git clone --depth 1 --single-branch https://github.com/apache/nuttx")
            if ret != 0:
                return ret

        # Get Nuttx-apps.
        if not os.path.exists("apps"):
            ret = os.system("git clone --depth 1 --single-branch https://github.com/apache/nuttx-apps apps")
            if ret != 0:
                return ret

        # Prepare environment.
        gcc_path    = os.path.join(os.path.abspath(toolchain_name), "bin")
        env         = os.environ.copy()
        env["PATH"] = f"{gcc_path}" + os.pathsep + env["PATH"]

        # Switch to NuttX directory.
        with switch_dir("nuttx"):
            # Configure Nuttx.
            ret = subprocess.run("./tools/configure.sh -E -l arty_a7:netnsh", shell=True, env=env) # FIXME: dynamics target and config
            if ret.returncode != 0:
                return ret

            # Build Nuttx Images.
            ret = subprocess.run("make CC=riscv-none-elf-gcc V=2 -j", shell=True, env=env)

            return ret.returncode

# FIXME: force /tftpboot cleanup ?
def nuttx_prepare_tftp(tftp_root=tftp_root):
    # Sanity check.
    for f in ["boot.json", "boot.bin"]:
        if os.path.exists(os.path.join(tftp_root, f)):
            os.remove(os.path.join(tftp_root, f))

    ret = os.system(f"cp third_party/nuttx/nuttx.bin {tftp_root}/boot.bin")
    return ret

def nuttx_copy_images(soc_json):
    base_dir   = os.path.dirname(soc_json)
    images_dir = os.path.join(base_dir, "images")

    # Create target directory
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    return os.system(f"cp third_party/nuttx/nuttx.bin {images_dir}/")

# Main ---------------------------------------------------------------------------------------------

def main():
    print("""
                                    __   _ __      _  __
                                   / /  (_) /____ | |/_/
                                  / /__/ / __/ -_)>  <
                                 /____/_/\\__/\\__/_/|_|
                              LiteX Hardware CI/NuttX Tests.

                      Copyright 2024 / Enjoy-Digital <enjoy-digital.fr>
""")
    description = "LiteX Hardware CI/NuttX Tests.\n\n"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

    # SoC Arguments.
    # --------------
    parser.add_argument("soc_json",                                  help="SoC JSON file.")

    # Build Arguments.
    # ----------------
    parser.add_argument("--clean",          action="store_true",     help="Clean Nuttx Build.")
    parser.add_argument("--build",          action="store_true",     help="Build Nuttx Images.")
    parser.add_argument("--prepare-tftp",   action="store_true",     help="Prepare/Copy Nuttx Images to TFTP root directory.")
    parser.add_argument("--copy-images",    action="store_true",     help="Copy Nuttx Images to target build directory.")

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

    # Nuttx Clean.
    # ------------
    if args.clean:
        if nuttx_clean() != 0:
            return ErrorCode.CLEAN_ERROR

    # Nuttx Build.
    # ------------
    if args.build:
        if nuttx_build() != 0:
            return ErrorCode.BUILD_ERROR

    # TFTP-Prepare.
    # -------------
    if args.prepare_tftp:
        if nuttx_prepare_tftp() != 0:
            return ErrorCode.TFTP_ERROR

    # Images Copy.
    # ------------
    if args.copy_images:
        if nuttx_copy_images(soc_json=args.soc_json) != 0:
            return ErrorCode.COPY_ERROR

    return ErrorCode.SUCCESS

if __name__ == "__main__":
    sys.exit(main())
