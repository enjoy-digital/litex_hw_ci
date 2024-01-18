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
        with serial.Serial(self.tty, self.tty_baudrate, timeout=1) as ser:
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
    "trellisboard:femtorv-std" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=femtorv --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:firev-std" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=firev --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-min" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv --cpu-variant=minimal --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-lite" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv --cpu-variant=lite --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-std" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv --cpu-variant=standard --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-full" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv --cpu-variant=full --integrated-main-ram-size=0x100",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-std-ddr3" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv --cpu-variant=full",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-smp-1-core-ddr3" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv_smp --cpu-count=1",
        tty     = "/dev/ttyUSB1",
    ),
    "trellisboard:vexriscv-smp-2-core-ddr3" : LiteXCIConfig(
        target  = "trellisboard",
        command = "--cpu-type=vexriscv_smp --cpu-count=2",
        tty     = "/dev/ttyUSB1",
    ),
}

# LiteX CI HTML report -----------------------------------------------------------------------------

def generate_html_report(report):
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LiteX CI Report</title>
        <style>
            body {{
                font-family: Arial, Helvetica, sans-serif;
                background-color: #222;
                color: #fff;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                font-size: 24px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background-color: #333;
                margin-top: 20px;
            }}
            th, td {{
                text-align: left;
                padding: 12px 15px;
                border-bottom: 1px solid #444;
                white-space: nowrap;
            }}
            th {{
                background-color: #444;
                color: #fff;
            }}
            tr:hover {{
                background-color: #555;
            }}
            .BUILD_ERROR {{
                color: red;
            }}
            .LOAD_ERROR {{
                color: red;
            }}
            .TEST_ERROR {{
                color: red;
            }}
            .NOT_RUN {{
                color: orange;
            }}
            .SUCCESS {{
                color: green;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LiteX CI Report</h1>
    """

    tests_executed = sum(1 for results in report.values() if any(status != LiteXCIStatus.NOT_RUN for status in results.values()))
    total_seconds = sum(float(results.get('Duration', '0.00 seconds')[:-7]) for results in report.values())

    # Convert total_seconds to hours, minutes, and seconds
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Add the summary line with the formatted total duration
    html_report += f"<p>Number of tests executed: {tests_executed} | Total Duration: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds</p>"

    html_report += """
            <table>
                <tr>
                    <th>Config</th>
                    <th>Time</th>
                    <th>Duration</th>
                    <th>Build</th>
                    <th>Load</th>
                    <th>Test</th>
                </tr>
    """

    for name, results in report.items():
        html_report += f"<tr><td>{name}</td>"
        time_value     = results.get('Time', '-')
        duration_value = results.get('Duration', '-')
        html_report += f"<td>{time_value}</td>"
        html_report += f"<td>{duration_value}</td>"
        for step, status in results.items():
            if step not in ['Time', 'Duration']:
                status_class = status.name
                html_report += f"<td class='{status_class}'>{status.name}</td>"
        html_report += "</tr>"

    html_report += """
            </table>
        </div>
    </body>
    </html>
    """

    with open('report.html', 'w') as html_file:
        html_file.write(html_report)
# LiteX CI Build/Test ------------------------------------------------------------------------------

steps  = ['build', 'load', 'test']
report = {name: {step.capitalize(): LiteXCIStatus.NOT_RUN for step in steps} for name in litex_ci_configs}

# Generate the initial HTML report
generate_html_report(report)

for name, config in litex_ci_configs.items():
    start_time = time.time()
    for step in steps:
        status = getattr(config, step)()
        report[name][step.capitalize()] = status
        if status != LiteXCIStatus.SUCCESS:
            break  # Skip remaining steps if the current step fails
    end_time = time.time()
    duration = end_time - start_time
    report[name]['Time']     = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    report[name]['Duration'] = f"{duration:.2f} seconds"

    # Update the HTML report after each configuration
    generate_html_report(report)

# LiteX CI Report ----------------------------------------------------------------------------------

print("\nLiteX CI Report:")
step_length = max(len(step) for step in steps)
for name, results in report.items():
    print(f"\n{name}:")
    for step, status in results.items():
        print(f"  {step.ljust(step_length)}: {status.name}")
