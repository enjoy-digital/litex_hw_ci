#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2026 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

"""Minimal YKUSH (Yepkit, 04d8:f2f7) control over libusb, as a stand-in for ykushcmd (needs pyusb and
read/write access to the device, see README).
Usage: ykush.py [--serial S] up|down|status [1|2|3|a]"""
import argparse, sys, usb.core, usb.util

CMD = {"down": 0x00, "up": 0x10, "status": 0x20}

def open_dev(serial=None):
    for d in usb.core.find(find_all=True, idVendor=0x04d8, idProduct=0xf2f7):
        if serial is None or usb.util.get_string(d, d.iSerialNumber) == serial:
            return d
    sys.exit("YKUSH not found")

def xfer(dev, cmd):
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
    intf = dev.get_active_configuration()[(0, 0)]
    ep_out = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
    ep_in  = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
    ep_out.write(bytes([cmd, cmd] + [0] * 62))
    return bytes(ep_in.read(64, timeout=1000))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--serial")
    p.add_argument("action", choices=CMD)
    p.add_argument("port", nargs="?", default="a")
    a = p.parse_args()
    dev = open_dev(a.serial)
    ports = [1, 2, 3] if a.port == "a" else [int(a.port)]
    if a.action != "status" and a.port == "a":
        r = xfer(dev, CMD[a.action] | 0x0a)
        print(a.action, "all", r[:2].hex())
        return
    for n in ports:
        r = xfer(dev, CMD[a.action] | n)
        if a.action == "status":
            # Reply: byte0 = 0x01 ok, byte1 = port state (0x1n up / 0x0n down) on current firmware.
            state = "up" if r[1] & 0x10 else "down"
            print(f"port {n}: {state} (raw {r[:2].hex()})")
        else:
            print(a.action, n, r[:2].hex())

if __name__ == "__main__":
    main()
