#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig, LiteXCITest, get_local_ip

# LiteX CI Config Definitions ----------------------------------------------------------------------

# Notes:
# Tested configs:
# - VexRiscv 32-bit / 1 Core / Wishbone Bus.
# - VexRiscv 32-bit / 2 Core / Wishbone Bus.
# - NaxRiscv 32-bit / 1 Core / Wishbone Bus.
# - NaxRiscv 64-bit / 1 Core / Wishbone Bus.

local_ip    = "192.168.1.50"
remote_ip   = get_local_ip()

tests = [
    LiteXCITest(send="reboot\n",                sleep=1),
    LiteXCITest(keyword="Memtest OK",           timeout=60.0),
    LiteXCITest(keyword="Network Test: OK",     timeout=60.0),
    LiteXCITest(keyword="Welcome to Buildroot", timeout=60.0),
]

exit_command        = "ykushcmd -d a"
arty_setup_command  = "ykushcmd -d a && ykushcmd -u 2"

litex_ci_configs = {
    # Digilent Arty running VexRiscv-SMP with:
    # - 1 Core.
    # - 8KB ICache (2-Ways).
    # - 8KB DCache (2-Ways).
    # - Coherent DMA.
    # - Ethernet 100Mbps.
    # - SPI-SDCard through Digilent PMOD on PMOD X formated as X.
    # - USB-Host through Machdyne PMOD on PMOD X formated as X.
    "arty:vexriscv-linux-1-core" : LiteXCIConfig(
        target           = "digilent_arty",
        gateware_command = f"--sys-clk-freq 100e6 \
        --cpu-type=vexriscv_smp --cpu-count=1 --cpu-variant=linux \
        --dcache-width=64 --dcache-size=8192 --dcache-ways=2 \
        --icache-width=64 --icache-size=8192 --icache-ways=2 \
        --dtlb-size=6 --with-coherent-dma --bus-bursting \
        --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip} \
        --with-spi-sdcard \
        --with-usb",
        software_command = "cd linux && python3 make.py ../build_arty_vexriscv-linux-1-core/soc.json --build --generate-dtb --prepare-tftp",
        setup_command    = arty_setup_command,
        exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),
    # Digilent Arty running VexRiscv-SMP with:
    # - 2 Cores.
    # - 8KB ICache (2-Ways).
    # - 8KB DCache (2-Ways).
    # - Coherent DMA.
    # - Ethernet 100Mbps.
    # - SPI-SDCard through Digilent PMOD on PMOD X formated as X.
    # - USB-Host through Machdyne PMOD on PMOD X formated as X.
    "arty:vexriscv-linux-2-core" : LiteXCIConfig(
        target           = "digilent_arty",
        gateware_command = f"--sys-clk-freq 100e6 \
        --cpu-type=vexriscv_smp --cpu-count=2 --cpu-variant=linux \
        --dcache-width=64 --dcache-size=8192 --dcache-ways=2 \
        --icache-width=64 --icache-size=8192 --icache-ways=2 \
        --dtlb-size=6 --with-coherent-dma --bus-bursting \
        --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip} \
        --with-spi-sdcard \
        --with-usb",
        software_command = "cd linux && python3 make.py ../build_arty_vexriscv-linux-2-core/soc.json --build --generate-dtb --prepare-tftp",
        setup_command    = arty_setup_command,
        exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),
    # Digilent Arty running NaxRiscv 32-bit with:
    # - 1 Core.
    # - Ethernet 100Mbps.
    # - Coherent DMA.
    # - Ethernet 100Mbps.
    # - SPI-SDCard through Digilent PMOD on PMOD X formated as X.
    # - USB-Host through Machdyne PMOD on PMOD X formated as X.
    "arty:naxriscv-linux-32-bit" : LiteXCIConfig(
        target           = "digilent_arty",
        gateware_command = f"--variant a7-100 --sys-clk-freq 100e6 \
        --cpu-type=naxriscv --scala-args='rvc=true,rvf=true,rvd=true' --with-rvc \
        --with-coherent-dma \
        --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip} \
        --with-spi-sdcard \
        --with-usb",
        software_command = "cd linux && python3 make.py ../build_arty_naxriscv-linux-32-bit/soc.json --build --generate-dtb --prepare-tftp",
        setup_command    = arty_setup_command,
        exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),
    # Digilent Arty running NaxRiscv 64-bit with:
    # - 1 Core.
    # - Ethernet 100Mbps.
    # - Coherent DMA.
    # - Ethernet 100Mbps.
    # - SPI-SDCard through Digilent PMOD on PMOD X formated as X.
    # - USB-Host through Machdyne PMOD on PMOD X formated as X.
    "arty:naxriscv-linux-64-bit" : LiteXCIConfig(
        target           = "digilent_arty",
        gateware_command = f"--variant a7-100 --sys-clk-freq 100e6 \
        --bus-standard axi-lite \
        --cpu-type=naxriscv --xlen 64 --scala-args='rvc=true,rvf=true,rvd=true' --with-rvc --with-fpu \
        --with-coherent-dma \
        --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip} \
        --with-spi-sdcard \
        --with-usb",
        software_command = "cd linux && python3 make.py ../build_arty_naxriscv-linux-64-bit/soc.json --build --generate-dtb --prepare-tftp",
        setup_command    = arty_setup_command,
        exit_command     = exit_command,
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),

}
