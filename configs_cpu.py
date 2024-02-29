#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig, LiteXCITest

# LiteX CI Config Definitions ----------------------------------------------------------------------

target = "digilent_arty"
tty    = "/dev/ttyUSB1"

litex_ci_configs = {
    "serv" : LiteXCIConfig(
        target           = target,
        gateware_command = "--cpu-type=serv --integrated-main-ram-size=0x100",
        tty              = tty,
    ),
    "femtorv" : LiteXCIConfig(
        target           = target,
        gateware_command = "--cpu-type=femtorv --integrated-main-ram-size=0x100",
        tty              = tty,
    ),
    "firev" : LiteXCIConfig(
        target           = target,
        gateware_command = "--cpu-type=firev --integrated-main-ram-size=0x100",
        tty              = tty,
    ),
    "kianv" : LiteXCIConfig(
        target           = target,
        gateware_command = "--cpu-type=kianv --integrated-main-ram-size=0x100",
        tty              = tty,
    ),
    "vexriscv" : LiteXCIConfig(
        target           = target,
        gateware_command = "--cpu-type=vexriscv --integrated-main-ram-size=0x100",
        tty              = tty,
    ),
    "picorv32" : LiteXCIConfig(
        target           = target,
        gateware_command = "--cpu-type=picorv32 --integrated-main-ram-size=0x100",
        tty              = tty,
    ),
    "neorv32" : LiteXCIConfig(
        target           = target,
        gateware_command = "--cpu-type=neorv32 --integrated-main-ram-size=0x100",
        tty              = tty,
    ),
    "ibex" : LiteXCIConfig(
        target           = target,
        gateware_command = "--cpu-type=ibex --integrated-main-ram-size=0x100",
        tty              = tty,
    ),
}
