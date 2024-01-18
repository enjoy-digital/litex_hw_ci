#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <hello@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import time
import enum
import shlex
import serial
import subprocess

# LiteX CI Config Constants ------------------------------------------------------------------------

class LiteXCIStatus(enum.IntEnum):
    SUCCESS     = 0
    BUILD_ERROR = 1
    LOAD_ERROR  = 2
    TEST_ERROR  = 3
    NOT_RUN     = 4

# LiteX CI Config ----------------------------------------------------------------------------------

class LiteXCIConfig:
    # Public.
    # -------
    def __init__(self, target="", command="", tty="", tty_baudrate=115200):
        self.target         = target
        self.command        = command
        self.tty            = tty
        self.tty_baudrate   = tty_baudrate

    def build(self):
        if self._run(f"python3 -m litex_boards.targets.{self.target} {self.command} --build"):
            return LiteXCIStatus.BUILD_ERROR
        return LiteXCIStatus.SUCCESS

    def load(self):
        if self._run(f"python3 -m litex_boards.targets.{self.target} {self.command} --load"):
            return LiteXCIStatus.LOAD_ERROR
        return LiteXCIStatus.SUCCESS

    def test(self, send="reboot\n", check="Memtest OK", timeout=5.0):
        with serial.Serial(self.tty, 115200, timeout=1) as ser:
                for cmd in send:
                    ser.write(bytes(cmd, "utf-8"))
                start_time = time.time()
                while (time.time() - start_time) < timeout:
                    data = ser.read(256)
                    print(data.decode('utf-8', errors='replace'), end='', flush=True)
                    if bytes(check, "utf-8") in data:
                        return LiteXCIStatus.SUCCESS
                return LiteXCIStatus.TEST_ERROR

    # Private.
    # --------
    def _run(self, command):
        process = subprocess.Popen(shlex.split(command),
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            text   = True
        )
        for line in process.stdout:
            print(line, end='')

        process.wait()
        return process.returncode

# LiteX CI Config Definitions ----------------------------------------------------------------------

litex_ci_configs = {
    "trellisboard:serv" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=serv --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:femtorv" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=femtorv --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
}

# LiteX CI Build/Test ------------------------------------------------------------------------------

steps  = ['build', 'load', 'test']
report = {name: {step.capitalize(): LiteXCIStatus.NOT_RUN.name for step in steps} for name in litex_ci_configs}

for name, config in litex_ci_configs.items():
    for step in steps:
        status = getattr(config, step)()
        report[name][step.capitalize()] = status.name
        if status != LiteXCIStatus.SUCCESS:
            break  # Skip remaining steps if the current step fails

# LiteX CI Report ----------------------------------------------------------------------------------

print("\nLiteX CI Report:")
step_length = max(len(step) for step in steps)
for name, results in report.items():
    print(f"\n{name}:")
    for step, status in results.items():
        print(f"  {step.ljust(step_length)}: {status}")
