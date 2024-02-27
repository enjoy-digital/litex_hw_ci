#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex_hw_ci import LiteXCIConfig

# LiteX CI Config Definitions ----------------------------------------------------------------------

# Notes:
# Tested configs:
# - VexRiscv 32-bit / 1 Core / Wishbone Bus.
# - VexRiscv 32-bit / 1 Core / AXI-Lite Bus.
# - VexRiscv 32-bit / 1 Core / AXI Bus.

local_ip    = "192.168.1.50"
remote_ip   = "192.168.1.121"
test_keywords = [
    "Memtest OK",
    "Network Test: OK",
    "MMC Test: OK",
    "USB Test: OK",
    "Welcome to Buildroot",
]
test_timeout = 60.0

litex_ci_configs = {
    # Diglent Arty running VexRiscv 32-bit with:
    # - Wishbone Bus.
    # - 1 Core.
    # - Coherent DMA.
    # - Ethernet 100Mbps.
    # - SPI-SDCard through Digilent PMOD on PMOD D formated as Fat32.
    # - USB-Host through Machdyne PMOD on PMOD A formated as Fat32.
    "arty_vexriscv_32_bit_wishbone" : LiteXCIConfig(
        target           = "digilent_arty",
        gateware_command = f"--sys-clk-freq 100e6 --bus-standard=wishbone \
        --cpu-type=vexriscv_smp --cpu-count=1 --cpu-variant=linux \
        --dcache-width=64 --dcache-size=8192 --dcache-ways=2 \
        --icache-width=64 --icache-size=8192 --icache-ways=2 \
        --dtlb-size=6 --with-coherent-dma --bus-bursting \
        --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip} \
        --with-spi-sdcard \
        --with-usb",
        software_command = f"cd linux && python3 make.py --soc-json=../build_arty_vexriscv_32_bit_wishbone/soc.json --linux-clean --linux-build --linux-generate-dtb --linux-prepare-tftp",
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        test_keywords    = test_keywords,
        test_timeout     = test_timeout,
    ),
    # Diglent Arty running VexRiscv 32-bit with:
    # - AXI-Lite Bus.
    # - 1 Core.
    # - Coherent DMA.
    # - Ethernet 100Mbps.
    # - SPI-SDCard through Digilent PMOD on PMOD D formated as Fat32.
    # - USB-Host through Machdyne PMOD on PMOD A formated as Fat32.
    "arty_vexriscv_32_bit_axi_lite" : LiteXCIConfig(
        target           = "digilent_arty",
        gateware_command = f"--sys-clk-freq 100e6 --bus-standard=axi-lite \
        --cpu-type=vexriscv_smp --cpu-count=1 --cpu-variant=linux \
        --dcache-width=64 --dcache-size=8192 --dcache-ways=2 \
        --icache-width=64 --icache-size=8192 --icache-ways=2 \
        --dtlb-size=6 --with-coherent-dma\
        --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip} \
        --with-spi-sdcard \
        --with-usb",
        software_command = f"cd linux && python3 make.py --soc-json=../build_arty_vexriscv_32_bit_axi_lite/soc.json --linux-clean --linux-build --linux-generate-dtb --linux-prepare-tftp",
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        test_keywords    = test_keywords,
        test_timeout     = test_timeout,
    ),
    # Diglent Arty running VexRiscv 32-bit with:
    # - AXI Bus.
    # - 1 Core.
    # - Coherent DMA.
    # - Ethernet 100Mbps.
    # - SPI-SDCard through Digilent PMOD on PMOD D formated as Fat32.
    # - USB-Host through Machdyne PMOD on PMOD A formated as Fat32.
    "arty_vexriscv_32_bit_axi" : LiteXCIConfig(
        target           = "digilent_arty",
        gateware_command = f"--sys-clk-freq 100e6 --bus-standard=axi \
        --cpu-type=vexriscv_smp --cpu-count=1 --cpu-variant=linux \
        --dcache-width=64 --dcache-size=8192 --dcache-ways=2 \
        --icache-width=64 --icache-size=8192 --icache-ways=2 \
        --dtlb-size=6 --with-coherent-dma\
        --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip} \
        --with-spi-sdcard \
        --with-usb",
        software_command = f"cd linux && python3 make.py --soc-json=../build_arty_vexriscv_32_bit_axi/soc.json --linux-clean --linux-build --linux-generate-dtb --linux-prepare-tftp",
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        test_keywords    = test_keywords,
        test_timeout     = test_timeout,
    ),
}
