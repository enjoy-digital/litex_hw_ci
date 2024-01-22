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
import argparse
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
        if self.tty == "":
            return LiteXCIStatus.LOAD_ERROR
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

# LiteX CI HTML report -----------------------------------------------------------------------------

def generate_html_report(report, report_filename):
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

    with open(report_filename, 'w') as html_file:
        html_file.write(html_report)

# LiteX CI Build/Test ------------------------------------------------------------------------------

def main():
    # Create an argument parser for the configuration file and report filename
    parser = argparse.ArgumentParser(description="LiteX HW CI")
    parser.add_argument("config", help="Path to the configuration file")
    parser.add_argument("--report", default="report.html", help="Filename for the HTML report (default: report.html)")
    args = parser.parse_args()

    # Import litex_ci_configs from the specified config file
    try:
        config_module = __import__(args.config.replace(".py", ""))
        litex_ci_configs = config_module.litex_ci_configs
    except ImportError:
        print(f"Error: Configuration file '{args.config}' not found or doesn't define 'litex_ci_configs'.")
        return

    steps = ['build', 'load', 'test']
    report = {name: {step.capitalize(): LiteXCIStatus.NOT_RUN for step in steps} for name in litex_ci_configs}

    generate_html_report(report, args.report)

    for name, config in litex_ci_configs.items():
        start_time = time.time()
        for step in steps:
            status = getattr(config, step)()
            report[name][step.capitalize()] = status
            if status != LiteXCIStatus.SUCCESS:
                break
        end_time = time.time()
        duration = end_time - start_time
        report[name]['Time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        report[name]['Duration'] = f"{duration:.2f} seconds"

        generate_html_report(report, args.report)

if __name__ == "__main__":
    main()
