#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig, LiteXCITest, get_local_ip

# LiteX CI Config Definitions ----------------------------------------------------------------------

# Notes:
# - LiteX Acorn Mini on YKUSH Kit Port 1.
# - Digilent Arty    on YKUSH Kit Port 2.
# - Orange Crab      on YKUSH Kit Port 3.

litex_ci_configs = {
    "acorn" : LiteXCIConfig(
        target           = "litex_acorn_baseboard_mini",
        setup_command    = "ykushcmd -d a && ykushcmd -u 1 && sleep 5",
        exit_command     = "ykushcmd -d a",
        tty              = "/dev/ttyUSB1",
    ),
    "arty" : LiteXCIConfig(
        target           = "digilent_arty",
        setup_command    = "ykushcmd -d a && ykushcmd -u 2 && sleep 5",
        exit_command     = "ykushcmd -d a",
        tty              = "/dev/ttyUSB1",
    ),
    "orangecrab" : LiteXCIConfig(
        target           = "gsd_orangecrab",
        gateware_command = f"--without-dfu-rst",
        setup_command    = "ykushcmd -d a && ykushcmd -u 3 && sleep 5",
        exit_command     = "ykushcmd -d a",
        tty              = "/dev/ttyACM0",
        test_delay       = 5,
    ),
}
