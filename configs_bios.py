#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig, LiteXCITest

# LiteX CI Config Definitions ----------------------------------------------------------------------

litex_ci_configs = {
    # TrellisBoard.
    "trellisboard_serv" : LiteXCIConfig(
        target           = "trellisboard",
        gateware_command = "--cpu-type=serv --integrated-main-ram-size=0x100",
        tty              = "/dev/ttyUSB1",
        tests            = [
            LiteXCITest(send="reboot\n",                                          sleep=1),
            LiteXCITest(send="ident\n", keyword="Ident:",                         sleep=1),
            LiteXCITest(send="help\n",  keyword="LiteX BIOS, available commands", sleep=1),
        ],
    ),
}


