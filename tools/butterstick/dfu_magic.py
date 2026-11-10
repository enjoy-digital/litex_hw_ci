#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2026 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

"""ButterStick: read (default) or program (--write) the bootloader magic word in SPI flash security
register 3, over Etherbone, through the LiteSPI master of the service image.
BL_MAGIC1 (0xc4f86d8a) = bootloader stays in DFU at every power-up and keeps the flag.
Same SPI sequences as butterstick-bootloader firmware/flash.c (0x48 read, 0x44 erase, 0x42 program)."""
import argparse, time
from litex import RemoteClient

BL_MAGIC1 = 0xc4f86d8a
SECREG3 = [0x00, 0x30, 0x00]  # security register 3 at 0x003000 (W25Q128JV)

p = argparse.ArgumentParser()
p.add_argument("--csr-csv", required=True)
p.add_argument("--port", type=int, default=1235)
p.add_argument("--write", action="store_true", help="Erase security register 3 and program BL_MAGIC1.")
a = p.parse_args()

bus = RemoteClient(csr_csv=a.csr_csv, port=a.port)
bus.open()
r = bus.regs

def xfer(byte):
    while not (r.spiflash_master_status.read() & 1): pass   # tx_ready
    r.spiflash_master_rxtx.write(byte)
    while not (r.spiflash_master_status.read() & 2): pass   # rx_ready
    return r.spiflash_master_rxtx.read() & 0xff

def cmd(bytes_out, n_in=0):
    r.spiflash_master_phyconfig.write(8 | (1 << 8) | (1 << 16))  # len=8, width=1, mask=1
    r.spiflash_master_cs.write(1)
    for b in bytes_out: xfer(b)
    data = [xfer(0) for _ in range(n_in)]
    r.spiflash_master_cs.write(0)
    return data

def status(): return cmd([0x05], 1)[0], cmd([0x35], 1)[0]
def wait_idle(t=5.0):
    end = time.time() + t
    while cmd([0x05], 1)[0] & 1:
        if time.time() > end: raise SystemExit("flash stays busy")
def read_secreg(): return cmd([0x48] + SECREG3 + [0x00], 16)  # + 1 dummy byte

jedec = cmd([0x9f], 3)
print("JEDEC id:", " ".join(f"{b:02x}" for b in jedec))
if jedec[0] != 0xef: raise SystemExit("not a Winbond flash: stop")
sr1, sr2 = status()
print(f"SR1={sr1:02x} SR2={sr2:02x} (SR2 LB3 lock bit = {(sr2 >> 5) & 1})")
print("secreg3[0:16]:", " ".join(f"{b:02x}" for b in read_secreg()))

if a.write:
    if (sr2 >> 5) & 1: raise SystemExit("security register 3 is locked (LB3): stop")
    cmd([0x06]); cmd([0x44] + SECREG3); wait_idle()                     # write enable + erase
    magic = list(BL_MAGIC1.to_bytes(4, "little"))
    cmd([0x06]); cmd([0x42] + SECREG3 + magic); wait_idle()             # write enable + program
    got = read_secreg()
    print("after write:", " ".join(f"{b:02x}" for b in got))
    print("MAGIC1 OK" if got[:4] == magic else "MAGIC1 MISMATCH")
bus.close()
