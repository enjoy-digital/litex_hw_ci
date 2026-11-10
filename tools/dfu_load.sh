#!/bin/sh
#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2026 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
#
# Load a bitstream through a DFU bootloader and reset the board so that it starts the new image.
# Usage: dfu_load.sh VID PID BITSTREAM ALT   (e.g. dfu_load.sh 1209 5af0 gsd_orangecrab.bit 0)
# ALT is required on purpose: it selects the flash partition. Check the board hint (boards/*.md)
# or the bootloader source: alt names shown by dfu-util can be misleading.
# Same sequence as litex.build.dfu.DFUProg. The final status read often fails with LIBUSB_ERROR_PIPE
# while the board reboots: this is expected and ignored.
set -e
[ $# -eq 4 ] || { echo "usage: $0 VID PID BITSTREAM ALT" >&2; exit 1; }
VID=$1; PID=$2; BIT=$3; ALT=$4
DFU=$(mktemp --suffix=.dfu)
cp "$BIT" "$DFU"
dfu-suffix -v "$VID" -p "$PID" -a "$DFU" > /dev/null
dfu-util -d "$VID:$PID" --download "$DFU" -R -a "$ALT" || true
rm -f "$DFU"
