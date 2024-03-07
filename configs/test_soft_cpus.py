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

litex_cpus = [
    #"blackparrot ", # (riscv   / softcore)
    #"cv32e40p    ", # (riscv   / softcore)
    #"cv32e41p    ", # (riscv   / softcore)
    #"cva5        ", # (riscv   / softcore)
    #"cva6        ", # (riscv   / softcore)
    "fazyrv      ", # (riscv   / softcore)
    "femtorv     ", # (riscv   / softcore)
    "firev       ", # (riscv   / softcore)
    "ibex        ", # (riscv   / softcore)
    "kianv       ", # (riscv   / softcore)
    #"lm32        ", # (lm32    / softcore)
    #"marocchino  ", # (or1k    / softcore)
    #"microwatt   ", # (ppc64   / softcore)
    #"minerva     ", # (riscv   / softcore)
    #"mor1kx      ", # (or1k    / softcore)
    "naxriscv    ", # (riscv   / softcore)
    "neorv32     ", # (riscv   / softcore)
    "openc906    ", # (riscv   / softcore)
    "picorv32    ", # (riscv   / softcore)
    "rocket      ", # (riscv   / softcore)
    "serv        ", # (riscv   / softcore)
    "vexriscv    ", # (riscv   / softcore)
    "vexriscv_smp", # (riscv   / softcore)
]

litex_ci_configs = {}
for litex_cpu in litex_cpus:
    litex_ci_config = LiteXCIConfig(
        target           = target,
        gateware_command = f"--cpu-type={litex_cpu} --integrated-main-ram-size=0x100",
        tty              = tty,
    )
    litex_ci_configs[litex_cpu] = litex_ci_config
