#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <hello@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig

# LiteX CI Config Definitions ----------------------------------------------------------------------

# Notes:
# Tested configs?:
# - VexRiscv-SMP with 1, 2, 4 cores?
# - VexRiscv-SMP with FPU?
# - NaxRiscv 32-bit with FPU?
# - NaxRiscv 64-bit with FPU?

litex_ci_configs = {
    # Digilent Arty running VexRiscv-SMP with:
    # - 1 Core.
    # - 8KB ICache (2-Ways).
    # - 8KB DCache (2-Ways).
    # - Coherent DMA.
    # - Ethernet 100Mbps.
    # - SPI-SDCard.
    # - USB-Host.
    "arty:vexriscv-linux-1-core" : LiteXCIConfig(
        target  = "digilent_arty",
        command = "--sys-clk-freq 100e6 \
        --cpu-type=vexriscv_smp --cpu-count=1 --cpu-variant=linux \
        --dcache-width=64 --dcache-size=8192 --dcache-ways=2 \
        --icache-width=64 --icache-size=8192 --icache-ways=2 \
        --dtlb-size=6 --with-coherent-dma --bus-bursting \
        --with-ethernet --eth-ip=192.168.1.50 --remote-ip=192.168.1.100 \
        --with-spi-sdcard \
        --with-usb",
        post_command = "cd linux && python3 make.py --cpu-type=vexriscv --soc-json=../build_arty_vexriscv-linux-1-core/soc.json --linux-build --linux-generate-dtb",
        #tty     = "/dev/ttyUSB1",
    ),
    # Digilent Arty running VexRiscv-SMP with:
    # - 2 Cores.
    # - 8KB ICache (2-Ways).
    # - 8KB DCache (2-Ways).
    # - Coherent DMA.
    # - Ethernet 100Mbps.
    # - SPI-SDCard.
    # - USB-Host.
    "arty:vexriscv-linux-2-core" : LiteXCIConfig(
        target  = "digilent_arty",
        command = "--sys-clk-freq 100e6 \
        --cpu-type=vexriscv_smp --cpu-count=1 --cpu-variant=linux \
        --dcache-width=64 --dcache-size=8192 --dcache-ways=2 \
        --icache-width=64 --icache-size=8192 --icache-ways=2 \
        --dtlb-size=6 --with-coherent-dma --bus-bursting \
        --with-ethernet --eth-ip=192.168.1.50 --remote-ip=192.168.1.100 \
        --with-spi-sdcard \
        --with-usb",
        #tty     = "/dev/ttyUSB1",
    ),
    # Digilent Arty running NaxRiscv 32-bit with:
    # - 1 Core.
    # - Ethernet 100Mbps.
    # - Coherent DMA.
    # - Ethernet 100Mbps.
    # - SPI-SDCard.
    # - USB-Host.
    "arty:naxriscv-linux-32-bit" : LiteXCIConfig(
        target  = "digilent_arty",
        command = "--sys-clk-freq 100e6 \
        --cpu-type=naxriscv --scala-args='rvc=true,rvf=true,rvd=true' --with-fpu --with-rvc \
        --with-ethernet --eth-ip=192.168.1.50 --remote-ip=192.168.1.100 \
        --with-spi-sdcard \
        --with-usb",
        #tty     = "/dev/ttyUSB1",
    ),
}
