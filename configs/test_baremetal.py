#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig

# LiteX CI Config Definitions ----------------------------------------------------------------------

exit_command               = "ykushcmd -d a"
trellisboard_setup_command = "ykushcmd -d a && ykushcmd -u 1"
arty_setup_command         = "ykushcmd -d a && ykushcmd -u 2"

litex_ci_configs = {
    # TrellisBoard.
    "trellisboard:serv" : LiteXCIConfig(
        target           = "trellisboard",
        gateware_command = "--cpu-type=serv --integrated-main-ram-size=0x100",
        setup_command    = trellisboard_setup_command,
        exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
    ),
    "trellisboard:femtorv-std" : LiteXCIConfig(
        target           = "trellisboard",
        gateware_command = "--cpu-type=femtorv --integrated-main-ram-size=0x100",
        setup_command    = trellisboard_setup_command,
        exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
    ),
    "trellisboard:firev-std" : LiteXCIConfig(
        target           = "trellisboard",
        gateware_command = "--cpu-type=firev --integrated-main-ram-size=0x100",
        setup_command    = trellisboard_setup_command,
        exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-min" : LiteXCIConfig(
        target           = "trellisboard",
        gateware_command = "--cpu-type=vexriscv --cpu-variant=minimal --integrated-main-ram-size=0x100",
        setup_command    = trellisboard_setup_command,
        exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-lite" : LiteXCIConfig(
        target           = "trellisboard",
        gateware_command = "--cpu-type=vexriscv --cpu-variant=lite --integrated-main-ram-size=0x100",
        setup_command    = trellisboard_setup_command,
        exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
    ),
    #"trellisboard:vexriscv-std" : LiteXCIConfig(
    #    target           = "trellisboard",
    #    gateware_command = "--cpu-type=vexriscv --cpu-variant=standard --integrated-main-ram-size=0x100",
    #    tty              = "/dev/ttyUSB1",
    #),
    #"trellisboard:vexriscv-full" : LiteXCIConfig(
    #    target           = "trellisboard",
    #    gateware_command = "--cpu-type=vexriscv --cpu-variant=full --integrated-main-ram-size=0x100",
    #    tty              = "/dev/ttyUSB1",
    #),
    #"trellisboard:vexriscv-std-ddr3" : LiteXCIConfig(
    #    target           = "trellisboard",
    #    gateware_command = "--cpu-type=vexriscv --cpu-variant=full",
    #    tty              = "/dev/ttyUSB1",
    #),
    #"trellisboard:vexriscv-smp-1-core-ddr3" : LiteXCIConfig(
    #    target           = "trellisboard",
    #    gateware_command = "--cpu-type=vexriscv_smp --cpu-count=1",
    #    tty              = "/dev/ttyUSB1",
    #),
    #"trellisboard:vexriscv-smp-2-core-ddr3" : LiteXCIConfig(
    #    target           = "trellisboard",
    #    gateware_command = "--cpu-type=vexriscv_smp --cpu-count=2",
    #    tty              = "/dev/ttyUSB1",
    #),
    # Digilent-Arty.
    "arty:vexriscv-all-peripherals" : LiteXCIConfig(
        target           = "digilent_arty",
        gateware_command = "--cpu-type=vexriscv --with-ethernet --with-sdcard --with-spi-flash",
        setup_command    = arty_setup_command,
        exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
    ),
    #"arty:naxriscv-32-all-peripherals" : LiteXCIConfig(
    #    target           = "digilent_arty",
    #    gateware_command = "--cpu-type=naxriscv --with-ethernet --with-sdcard --with-spi-flash",
    #    tty              = "/dev/ttyUSB1",
    #),
    ## SQRL-XCU1525.
    #"xcu1525:vexriscv-all-peripherals" : LiteXCIConfig(
    #    target           = "sqrl_xcu1525",
    #    gateware_command = "--cpu-type=vexriscv",
    #    tty              = "/dev/ttyUSB1",
    #),
    #"xcu1525:naxriscv-32-all-peripherals" : LiteXCIConfig(
    #    target           = "sqrl_xcu1525",
    #    gateware_command = "--cpu-type=naxriscv",
    #    tty             = "/dev/ttyUSB1",
    #),
}


