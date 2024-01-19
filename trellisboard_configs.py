#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <hello@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig

# LiteX CI Config Definitions ----------------------------------------------------------------------

litex_ci_configs = {
    "trellisboard:serv" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=serv --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:femtorv-std" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=femtorv --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:firev-std" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=firev --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-min" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv --cpu-variant=minimal --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-lite" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv --cpu-variant=lite --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-std" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv --cpu-variant=standard --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-full" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv --cpu-variant=full --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-std-ddr3" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv --cpu-variant=full",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-smp-1-core-ddr3" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv_smp --cpu-count=1",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-smp-2-core-ddr3" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv_smp --cpu-count=2",
        tty     = "/dev/ttyUSB1",
    ),
}

