#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <hello@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig

# LiteX CI Config Definitions ----------------------------------------------------------------------

litex_ci_configs = {
    "arty:vexriscv-linux" : LiteXCIConfig(
        target  = "digilent_arty",
        command = "--sys-clk-freq 100e6 --cpu-type=vexriscv_smp --cpu-variant=linux \
        --dcache-width=64 --dcache-size=8192 --dcache-ways=2 \
        --icache-width=64 --icache-size=8192 --icache-ways=2 \
        --dtlb-size=6 --with-coherent-dma --bus-bursting \
        --with-ethernet \
        --with-spi-sdcard",
        #tty     = "/dev/ttyUSB1",
    ),
}
