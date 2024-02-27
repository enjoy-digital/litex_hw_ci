#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig

# LiteX CI Config Definitions ----------------------------------------------------------------------

local_ip    = "192.168.1.50"
remote_ip   = "192.168.1.121"
test_keywords = [
    "Memtest OK",
    "Starting network: OK",
    "Network Test: OK",
    "Welcome to Buildroot",
]
test_timeout = 60.0

fixme = 32

litex_ci_configs = {
    # Acorn Baseboard Mini running NaxRiscv-32-bit with:
    # - 1 Core.
    # - FPU.
    # - Coherent DMA.
    # - Ethernet 1000Mbps.
    "acorn_baseboard_mini_naxriscv_32_bit" : LiteXCIConfig(
        target           = "litex_acorn_baseboard_mini",
        gateware_command = f"--sys-clk-freq 100e6 \
        --cpu-type=naxriscv --xlen 32 --scala-args='rvc=true,rvf=true,rvd=true' --with-rvc --with-fpu \
        --with-coherent-dma \
        --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip}",
        software_command = f"cd linux && python3 make.py --cpu-type=naxriscv --xlen 32 --soc-json=../build_acorn_baseboard_mini_naxriscv_32_bit/soc.json --linux-clean --linux-build --linux-generate-dtb --linux-prepare-tftp",
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        test_keywords    = test_keywords,
        test_timeout     = test_timeout,
    ),
    # Acorn Baseboard Mini running NaxRiscv-64-bit with:
    # - 1 Core.
    # - FPU.
    # - Coherent DMA.
    # - Ethernet 1000Mbps.
    "acorn_baseboard_mini_naxriscv_64_bit" : LiteXCIConfig(
        target           = "litex_acorn_baseboard_mini",
        gateware_command = f"--sys-clk-freq 100e6 \
        --cpu-type=naxriscv --xlen 64 --scala-args='rvc=true,rvf=true,rvd=true' --with-rvc --with-fpu \
        --with-coherent-dma \
        --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip}",
        software_command = f"cd linux && python3 make.py --cpu-type=naxriscv --xlen 64 --soc-json=../build_acorn_baseboard_mini_naxriscv_64_bit/soc.json --linux-clean --linux-build --linux-generate-dtb --linux-prepare-tftp",
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        test_keywords    = test_keywords,
        test_timeout     = test_timeout,
    ),
}
