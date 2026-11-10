#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2026 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

"""Block-by-block DFU download with status polling after each block (pyusb), then manifest + reset.
Usage: dfu_write.py VID PID ALT FILE [DELAY_MS] (VID/PID in hex; DELAY_MS pauses between blocks). Stops at the first block that times out or
reports an error. Used where dfu-util fails (ButterStick bootloader, see boards/gsd_butterstick.md)."""
import sys, time, usb.core, usb.util
vid, pid, alt, path = int(sys.argv[1], 16), int(sys.argv[2], 16), int(sys.argv[3]), sys.argv[4]
delay = float(sys.argv[5]) / 1000 if len(sys.argv) > 5 else 0.0
data = open(path, "rb").read()
d = usb.core.find(idVendor=vid, idProduct=pid)
if d is None: sys.exit("no device")
def st(): return list(d.ctrl_transfer(0xA1, 3, 0, 0, 6, timeout=10000))
try:
    if d.is_kernel_driver_active(0): d.detach_kernel_driver(0)
except Exception: pass
usb.util.claim_interface(d, 0)
d.set_interface_altsetting(0, alt)
s = st()
if s[4] == 10: d.ctrl_transfer(0x21, 4, 0, 0, None); s = st()
print("start", s, flush=True)
bs = 512; n = (len(data) + bs - 1) // bs; t = time.time()
for b in range(n):
    try:
        d.ctrl_transfer(0x21, 1, b, 0, data[b*bs:(b+1)*bs], timeout=10000)
        while True:
            s = st()
            if s[4] != 4: break
            time.sleep(0.002)
    except Exception as e:
        print("block", b, "of", n, "ERR", e, "%.1fs" % (time.time() - t)); sys.exit(1)
    if s[0] != 0 or s[4] != 5:
        print("block", b, "bad status", s); sys.exit(1)
    if delay: time.sleep(delay)
    if b % 100 == 0: print("block", b, "ok %.1fs" % (time.time() - t), flush=True)
print("all", n, "blocks ok %.1fs" % (time.time() - t), flush=True)
d.ctrl_transfer(0x21, 1, n, 0, b"", timeout=10000)
try: print("manifest", st())
except Exception as e: print("manifest status:", e)
try: d.reset()
except Exception as e: print("reset:", e)
