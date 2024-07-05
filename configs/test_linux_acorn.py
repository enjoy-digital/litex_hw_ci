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
# - VexRiscv 32-bit / Wishbone Bus / 4 cores.
# - NaxRiscv 32-bit / Wishbone Bus / FPU.
# - NaxRiscv 32-bit / AXI-Lite Bus / FPU.
# - NaxRiscv 64-bit / Wishbone Bus / FPU.
# - NaxRiscv 64-bit / AXI-Lite Bus / FPU.

local_ip    = "192.168.1.50"
remote_ip   = get_local_ip()

linux_build_args = "--clean --build --generate-dtb --prepare-tftp --copy-images"

tests = [
    LiteXCITest(send="reboot\n",                sleep=1),
    LiteXCITest(keyword="Memtest OK",           timeout=60.0),
    LiteXCITest(keyword="Network Test: OK",     timeout=60.0),
    LiteXCITest(keyword="Welcome to Buildroot", timeout=60.0),
]

litex_ci_configs = {
    # Acorn Baseboard Mini running VexRiscv 32-bit with:
    # - Wishbone Bus.
    # - 4 Core.
    # - FPU.
    # - Coherent DMA.
    # - 1Gbps Ethernet / 1000BaseX with SFP module.
    "acorn_vexriscv_32_bit_4_cores_wishbone" : LiteXCIConfig(
        target           = "litex_acorn_baseboard_mini",
        gateware_command = f"--sys-clk-freq 100e6 --bus-standard=wishbone \
        --cpu-type=vexriscv_smp --cpu-count=4 --cpu-variant=linux \
        --dcache-width=64 --dcache-size=8192 --dcache-ways=2 \
        --icache-width=64 --icache-size=8192 --icache-ways=2 \
        --dtlb-size=6 --with-coherent-dma --bus-bursting --with-rvc --with-fpu \
        --with-sata --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip}",
        software_command = "cd linux && python3 make.py {output_dir}/soc.json " + linux_build_args,
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),
    # Acorn Baseboard Mini running NaxRiscv-32-bit with:
    # - Wishbone Bus.
    # - 1 Core.
    # - FPU.
    # - Coherent DMA.
    # - 1Gbps Ethernet / 1000BaseX with SFP module.
    "acorn_naxriscv_32_bit_wishbone" : LiteXCIConfig(
        target           = "litex_acorn_baseboard_mini",
        gateware_command = f"--sys-clk-freq 100e6 --bus-standard=wishbone \
        --cpu-type=naxriscv --xlen 32 --scala-args='rvc=true,rvf=true,rvd=true' --with-rvc --with-fpu \
        --with-coherent-dma \
        --with-sata --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip}",
        software_command = "cd linux && python3 make.py {output_dir}/soc.json " + linux_build_args,
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),
    # Acorn Baseboard Mini running NaxRiscv-32-bit with:
    # - AXI-Lite Bus.
    # - 1 Core.
    # - FPU.
    # - Coherent DMA.
    # - 1Gbps Ethernet / 1000BaseX with SFP module.
    "acorn_naxriscv_32_bit_axi_lite" : LiteXCIConfig(
        target           = "litex_acorn_baseboard_mini",
        gateware_command = f"--sys-clk-freq 100e6 --bus-standard=axi-lite \
        --cpu-type=naxriscv --xlen 32 --scala-args='rvc=true,rvf=true,rvd=true' --with-rvc --with-fpu \
        --with-coherent-dma \
        --with-sata --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip}",
        software_command = "cd linux && python3 make.py {output_dir}/soc.json " + linux_build_args,
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),
    # Acorn Baseboard Mini running NaxRiscv-64-bit with:
    # - Wishbone Bus.
    # - 1 Core.
    # - FPU.
    # - Coherent DMA.
    # - 1Gbps Ethernet / 1000BaseX with SFP module.
    "acorn_naxriscv_64_bit_wishbone" : LiteXCIConfig(
        target           = "litex_acorn_baseboard_mini",
        gateware_command = f"--sys-clk-freq 100e6 --bus-standard=wishbone \
        --cpu-type=naxriscv --xlen 64 --scala-args='rvc=true,rvf=true,rvd=true' --with-rvc --with-fpu \
        --with-coherent-dma \
        --with-sata --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip}",
        software_command = "cd linux && python3 make.py {output_dir}/soc.json " + linux_build_args,
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),
    # Acorn Baseboard Mini running NaxRiscv-64-bit with:
    # - AXI-Lite Bus.
    # - 1 Core.
    # - FPU.
    # - Coherent DMA.
    # - 1Gbps Ethernet / 1000BaseX with SFP module.
    "acorn_naxriscv_64_bit_axi_lite" : LiteXCIConfig(
        target           = "litex_acorn_baseboard_mini",
        gateware_command = f"--sys-clk-freq 100e6 --bus-standard=axi-lite \
        --cpu-type=naxriscv --xlen 64 --scala-args='rvc=true,rvf=true,rvd=true' --with-rvc --with-fpu \
        --with-coherent-dma \
        --with-sata --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip}",
        software_command = "cd linux && python3 make.py {output_dir}/soc.json " + linux_build_args,
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),
    # Acorn Baseboard Mini running Rocket with:
    # - 1 Core
    # - Ethernet - 1Gbps Ethernet / 1000BaseX with SFP module.
    "acorn_rocket_1_core" : LiteXCIConfig(
        target           = "litex_acorn_baseboard_mini",
        gateware_command = f"--sys-clk-freq 75e6 \
        --cpu-type=rocket --cpu-num-cores=1 --cpu-mem-width=2 --cpu-variant=linux \
        --with-sata --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip}",
        software_command = "cd linux && python3 make.py {output_dir}/soc.json " + linux_build_args,
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),
    # Acorn Baseboard Mini running VexiiRiscv-32-bit with:
    # - AXI-Lite Bus.
    # - 1 Core.
    # - FPU.
    # - Coherent DMA.
    # - 1Gbps Ethernet / 1000BaseX with SFP module.
    "acorn_vexiiriscv_32_bit_axi_lite" : LiteXCIConfig(
        target           = "litex_acorn_baseboard_mini",
        gateware_command = f"--sys-clk-freq 100e6 --bus-standard=axi-lite \
        --cpu-type=vexiiriscv --cpu-variant=linux \
        --with-coherent-dma \
        --with-sata --with-ethernet --eth-ip={local_ip} --remote-ip={remote_ip}",
        software_command = "cd linux && python3 make.py {output_dir}/soc.json " + linux_build_args,
        setup_command    = "",
        exit_command     = "",
        tty              = "/dev/ttyUSB1",
        tests            = tests,
    ),
}
