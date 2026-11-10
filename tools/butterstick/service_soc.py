#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2026 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# ButterStick "service" image: default target + Etherbone + SPI flash with the raw SPI master CSRs
# (litex-boards uses with_master=False). Used to program the bootloader magic word in flash
# security register 3 over Etherbone.
import sys
from litex.soc.integration.soc import LiteXSoC
_add = LiteXSoC.add_spi_flash
def add_spi_flash(self, *a, **kw):
    kw["with_master"] = True
    return _add(self, *a, **kw)
LiteXSoC.add_spi_flash = add_spi_flash
from litex_boards.targets import gsd_butterstick
sys.exit(gsd_butterstick.main())
