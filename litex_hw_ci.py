#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <hello@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import re
import time
import enum
import shlex
import serial
import argparse
import subprocess
from pathlib import Path

# LiteX CI Config Constants

class LiteXCIStatus(enum.IntEnum):
    SUCCESS = 0
    BUILD_ERROR = 1
    LOAD_ERROR = 2
    TEST_ERROR = 3
    NOT_RUN = 4

# Utility Functions

def execute_command(command, log_path):
    with open(log_path, "w") as log_file:
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end='')
            log_file.write(line)
    return process.wait() == 0

def prepare_directory(name):
    log_dir = Path(f"build_{name}")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

# LiteX CI Config

class LiteXCIConfig:
    def __init__(self, target="", gateware_command="", software_command="", tty="", tty_baudrate=115200, test_checks=["Memtest OK"], test_timeout=5.0):
        self.target = target
        self.gateware_command = gateware_command
        self.software_command = software_command
        self.tty = tty
        self.tty_baudrate = tty_baudrate
        self.test_checks = test_checks
        self.test_timeout = test_timeout

    def set_name(self, name=""):
        assert not hasattr(self, "name")
        self.name = name

    def perform_step(self, step_name, command, log_filename_suffix):
        log_dir = prepare_directory(self.name)
        log_path = log_dir / f"{log_filename_suffix}.rpt"
        if execute_command(command, log_path):
            return LiteXCIStatus.SUCCESS
        return getattr(LiteXCIStatus, f"{step_name.upper()}_ERROR")

    def gateware_build(self):
        command = f"python3 -m litex_boards.targets.{self.target} {self.gateware_command} --output-dir=build_{self.name} --soc-json=build_{self.name}/soc.json --build"
        return self.perform_step("build", command, "gateware_build")

    def software_build(self):
        if self.software_command == "":
            return LiteXCIStatus.NOT_RUN
        command = self.software_command
        return self.perform_step("build", command, "software_build")

    def load(self):
        command = f"python3 -m litex_boards.targets.{self.target} {self.gateware_command} --output-dir=build_{self.name} --load"
        return self.perform_step("load", command, "load")

    def test(self, send="reboot\n"):
        log_dir = prepare_directory(self.name)
        log_path = log_dir / "test.rpt"
        status = LiteXCIStatus.TEST_ERROR
        with serial.Serial(self.tty, self.tty_baudrate, timeout=1) as ser, open(log_path, "w") as log_file:
            ser.write(bytes(send, "utf-8"))
            log_file.write(send)
            start_time = time.time()
            accumulated_data = ""
            while time.time() - start_time < self.test_timeout:
                data = ser.read(256).decode('utf-8', errors='replace')
                if data:
                    print(data, end='', flush=True)
                    log_file.write(data)
                    accumulated_data += data
                    if all(check in accumulated_data for check in self.test_checks):
                        status = LiteXCIStatus.SUCCESS
                        break
        return status


# LiteX CI HTML report -----------------------------------------------------------------------------

def generate_html_report(report, report_filename, steps):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LiteX CI Report</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #121212;
                color: #e0e0e0;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 960px;
                margin: 20px auto;
                background: #1e1e1e;
                box-shadow: 0 2px 4px rgba(0,0,0,0.5);
                padding: 20px;
                border-radius: 8px;
            }}
            h1 {{
                color: #e0e0e0;
                font-size: 24px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                text-align: left;
                padding: 12px 15px;
                border: 1px solid #333;
            }}
            th {{
                background-color: #2c2c2c;
                color: #ffffff;
            }}
            tr:nth-child(even) {{
                background-color: #262626;
            }}
            .status {{
                font-weight: bold;
            }}
            .status-SUCCESS {{
                color: #4CAF50; /* Green for success */
            }}
            .status-BUILD_ERROR, .status-LOAD_ERROR, .status-TEST_ERROR {{
                color: #F44336; /* Red for errors */
            }}
            .status-NOT_RUN {{
                color: #FF9800; /* Orange for not run */
            }}
            a {{
                color: #76B900; /* Adjusted for visibility in dark mode */
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LiteX CI Report</h1>
            {generate_summary(report)}
            {generate_table(report, steps)}
        </div>
    </body>
    </html>
    """

    with open(report_filename, 'w') as file:
        file.write(html_content)

def generate_summary(report):
    tests_executed = sum(1 for results in report.values() if any(status != LiteXCIStatus.NOT_RUN for status in results.values()))
    total_seconds = sum(float(results.get('Duration', '0.00 seconds')[:-7]) for results in report.values())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    summary_content = f"<p>Number of tests executed: {tests_executed} | Total Duration: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds</p>"
    return summary_content

def generate_table(report, steps):
    table_html = """
        <table>
            <tr>
                <th>Config</th>
                <th>Time</th>
                <th>Duration</th>
                <th>Gateware Build</th>
                <th>Software Build</th>
                <th>Load</th>
                <th>Test</th>
            </tr>
    """
    for name, results in report.items():
        table_html += f"<tr><td>{name}</td>"
        time_value = results.get('Time', '-')
        duration_value = results.get('Duration', '-')
        table_html += f"<td>{time_value}</td><td>{duration_value}</td>"
        for step in steps:
            status = results.get(step.capitalize(), LiteXCIStatus.NOT_RUN)
            status_class = f"status-{status.name}"
            log_filename = f"build_{name}/{step}.rpt"
            if status != LiteXCIStatus.NOT_RUN:
                table_html += f"<td class='{status_class}'><a href='{log_filename}' target='_blank'>{status.name}</a></td>"
            else:
                table_html += f"<td class='{status_class}'>{status.name}</td>"
        table_html += "</tr>"
    table_html += "</table>"
    return table_html


# LiteX CI Build/Test ------------------------------------------------------------------------------

def format_name(name):
    return re.sub(r'[^\w-]', '_', name)

def main():
    parser = argparse.ArgumentParser(description="LiteX HW CI")
    parser.add_argument("configs_file",                    help="Path to the configurations file.")
    parser.add_argument("--report", default="report.html", help="Filename for the HTML report (default: report.html).")
    parser.add_argument("--config",                        help="Select specific configuration from file (optional).")
    parser.add_argument("--list", action="store_true",     help="List all available configurations in file and exit.")
    args = parser.parse_args()

    # Import litex_ci_configs from the specified config file
    try:
        config_module = __import__(args.configs_file.replace(".py", "").replace("/", "."), fromlist=[''])
        litex_ci_configs = config_module.litex_ci_configs
    except ImportError as e:
        print(f"Error: {e}\nConfigurations file '{args.config_file}' not found or doesn't define 'litex_ci_configs'.")
        return

    # If --list is specified, print the configurations and exit.
    if args.list:
        print("Available configurations:")
        for name in litex_ci_configs:
            print(f"- {name}")
        return

    # If --config is specified, only execute this configuration.
    if args.config:
        if args.config not in litex_ci_configs:
            print(f"Error: Configuration '{args.config}' not found.")
            return
        litex_ci_configs = {args.config: litex_ci_configs[args.config]}

    steps = ['gateware_build', 'software_build', 'load', 'test']
    report = {format_name(name): {step.capitalize(): LiteXCIStatus.NOT_RUN for step in steps} for name in litex_ci_configs}

    generate_html_report(report, args.report, steps)

    for name, config in litex_ci_configs.items():
        name = format_name(name)
        config.set_name(name)
        start_time = time.time()
        for step in steps:
            status = getattr(config, step)()
            report[name][step.capitalize()] = status
            if status not in [LiteXCIStatus.SUCCESS, LiteXCIStatus.NOT_RUN]:
                break
        end_time = time.time()
        duration = end_time - start_time
        report[name]['Time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        report[name]['Duration'] = f"{duration:.2f} seconds"

        generate_html_report(report, args.report, steps)

if __name__ == "__main__":
    main()

