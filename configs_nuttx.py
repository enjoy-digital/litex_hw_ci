#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig

# LiteX CI Config Definitions ----------------------------------------------------------------------

# Notes:
# Tested configs?:
# - VexRiscv-SMP with 1, 2, 4 cores?
# - VexRiscv-SMP with FPU?
# - NaxRiscv 32-bit with FPU?
# - NaxRiscv 64-bit with FPU?

local_ip    = "192.168.1.50"
remote_ip   = "192.168.1.128"
test_keywords = [
    "Memtest OK",
    "NuttShell (NSH)",
]
test_timeout = 60.0

exit_command        = "ykushcmd -d a"
arty_setup_command  = "ykushcmd -d a && ykushcmd -u 2"

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
        #setup_command    = arty_setup_command,
        #exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
        tty_baudrate     = 1000000,
        test_keywords    = test_keywords,
        test_timeout     = test_timeout
    ),
}
