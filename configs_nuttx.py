#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig, LiteXCITest

# LiteX CI Config Definitions ----------------------------------------------------------------------

# Notes:
# Tested configs?:
# - VexRiscv-SMP with 1, 2, 4 cores?
# - VexRiscv-SMP with FPU?
# - NaxRiscv 32-bit with FPU?
# - NaxRiscv 64-bit with FPU?

local_ip    = "192.168.1.50"
remote_ip   = "192.168.1.128"
tests = [
    LiteXCITest(send="reboot\n",           sleep=1),
    LiteXCITest(keyword="Memtest OK",      timeout=60.0),
    LiteXCITest(keyword="NuttShell (NSH)", timeout=60.0),
    LiteXCITest(send=f"ifconfig eth0 {local_ip}\n", timeout=10.0),
    LiteXCITest(send=f"ping {remote_ip}\n", keyword="10 packets transmitted, 10 received, 0% packet loss", timeout=60.0),
]

litex_ci_configs = {
    # Digilent Arty running VexRiscv with:
    # - Ethernet 100Mbps.
    # - SDCard through Digilent PMOD on PMOD X formated as X (for memory map reason SPI-SDCard can't be used).
    "arty:vexriscv-secure-1-core" : LiteXCIConfig(
        target           = "digilent_arty",
        gateware_command = f"--sys-clk-freq 100e6 \
        --uart-baudrate 1000000 \
        --cpu-type=vexriscv --cpu-variant=secure \
        --bus-bursting \
        --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip} \
        --with-sdcard",
        software_command = "cd nuttx && python3 make.py --nuttx-clean --nuttx-build --nuttx-prepare-tftp",
        tty              = "/dev/ttyUSB1",
        tty_baudrate     = 1000000,
        tests            = tests,
    ),
}
