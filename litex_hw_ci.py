#!/usr/bin/env python3

#
# This file is part of LiteX-HW-CI.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import re
import time
import enum
import shlex
import serial
import socket
import datetime
import argparse
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

# Helpers ------------------------------------------------------------------------------------------

def get_local_ip():
    return socket.gethostbyname(socket.gethostname())

# LiteX CI Config Constants ------------------------------------------------------------------------

class LiteXCIStatus(enum.IntEnum):
    SUCCESS     = 0
    BUILD_ERROR = 1
    LOAD_ERROR  = 2
    TEST_ERROR  = 3
    NOT_RUN     = 4

# LiteX CI Test ------------------------------------------------------------------------------------

class LiteXCITest:
    def __init__(self, send="", keyword=None, timeout=5.0, sleep=0.0):
        self.send    = send
        self.keyword = keyword
        self.timeout = timeout
        self.sleep   = sleep

# LiteX CI Helpers ---------------------------------------------------------------------------------

def execute_command(command, log_path, shell=False):
    with open(log_path, "w") as log_file:
        if not shell:
            command = shlex.split(command)
        process = subprocess.Popen(command,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            text   = True,
            shell  = shell
        )
        for line in process.stdout:
            print(line, end='')
            log_file.write(line)
    return process.wait() == 0

def prepare_directory(name):
    dst_dir = Path(f"build_{name}")
    dst_dir.mkdir(parents=True, exist_ok=True)
    return dst_dir

# LiteX CI Config ----------------------------------------------------------------------------------

class LiteXCIConfig:
    def __init__(self, target="",
        gateware_command = "",
        software_command = "",
        setup_command    = "",
        exit_command     = "",
        tty              = "", tty_baudrate=115200,
        tests            = [LiteXCITest(send="reboot", keyword="Memtest OK", timeout=5.0)],
    ):
        # Target Parameters.
        self.target           = target

        # Commands Parameters.
        self.gateware_command = gateware_command
        self.software_command = software_command
        self.setup_command    = setup_command
        self.exit_command     = exit_command

        # TTY Parameters.
        self.tty              = tty
        self.tty_baudrate     = tty_baudrate

        # Tests.
        self.tests            = tests

    def set_name(self, name=""):
        assert not hasattr(self, "name")
        self.name = name

    def perform_step(self, step_name, command, log_filename_suffix, shell=False):
        dst_dir  = prepare_directory(self.name)
        log_path = os.path.join(dst_dir, f"{log_filename_suffix}.rpt")
        if execute_command(command, log_path, shell):
            return LiteXCIStatus.SUCCESS
        return getattr(LiteXCIStatus, f"{step_name.upper()}_ERROR")

    def firmware_build(self):
        command = f"python3 -m litex_boards.targets.{self.target} {self.gateware_command} \
        --output-dir=build_{self.name} \
        --soc-json=build_{self.name}/soc.json \
        --build --no-compile-gateware"
        return self.perform_step("build", command, "firmware_build")

    def gateware_build(self):
        command = f"python3 -m litex_boards.targets.{self.target} {self.gateware_command} \
        --output-dir=build_{self.name} \
        --build"
        return self.perform_step("build", command, "gateware_build")

    def software_build(self):
        if self.software_command == "":
            return LiteXCIStatus.NOT_RUN
        r = self.perform_step("build", self.software_command, "software_build", shell=True)
        return r

    def setup(self):
        if self.setup_command == "":
            return LiteXCIStatus.NOT_RUN
        os.system(self.setup_command) # FIXME.
        return LiteXCIStatus.SUCCESS

    def load(self):
        command = f"python3 -m litex_boards.targets.{self.target} {self.gateware_command} \
        --output-dir=build_{self.name} \
        --load"
        return self.perform_step("load", command, "load")

    def test(self):
        dst_dir  = prepare_directory(self.name)
        log_path = os.path.join(dst_dir, "test.rpt")
        status = LiteXCIStatus.TEST_ERROR

        # Open TTY and log file.
        with serial.Serial(self.tty, self.tty_baudrate, timeout=1) as ser, open(log_path, "w") as log_file:
            start_time = time.time()

            # Iterate on Tests.
            for test in self.tests:

                # Send Commands.
                ser.write(bytes(test.send, "utf-8"))

                # Receive/Check Keywords.
                if test.keyword is not None:
                    _data = ""
                    while time.time() - start_time < test.timeout:
                        data = ser.read().decode('utf-8', errors='replace')
                        if data:
                            print(data, end='', flush=True)
                            log_file.write(data)
                            _data += data
                            if test.keyword in _data:
                                if test is self.tests[-1]:
                                    status = LiteXCIStatus.SUCCESS
                                break
                # Sleep.
                time.sleep(test.sleep)

        return status

    def exit(self):
        if self.exit_command == "":
            return LiteXCIStatus.NOT_RUN
        os.system(self.exit_command) # FIXME.
        return LiteXCIStatus.SUCCESS

# LiteX CI HTML report -----------------------------------------------------------------------------

def enum_to_str(enum_val):
    if isinstance(enum_val, LiteXCIStatus) and (enum_val == LiteXCIStatus.NOT_RUN):
        return "-"
    elif isinstance(enum_val, enum.Enum):
        return enum_val.name
    return str(enum_val)

def generate_html_report(report, report_filename, steps, start_time, config_file):
    env      = Environment(loader=FileSystemLoader(searchpath='./'))
    template = env.get_template('html/report_template.html')

    # Convert Enum values to strings.
    for name, results in report.items():
        for step in steps:
            step_key = step.capitalize()
            if step_key in results:
                results[step_key] = enum_to_str(results[step_key])

    # Prepare summary information.
    tests_executed    = sum(1 for results in report.values() if any(status != '-' for status in results.values()))
    total_seconds     = sum(float(results.get('Duration', '0.00 seconds')[:-7]) for results in report.values())
    hours, remainder  = divmod(total_seconds, 3600)
    minutes, seconds  = divmod(remainder, 60)
    summary  = f"<p>Build Start Time: {start_time} | Configs File: {config_file}</p>"
    summary += f"<p>Number of tests executed: {tests_executed} | Total Duration: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds</p>"

    # Render the HTML template with the report data and summary.
    html_content = template.render(report=report, steps=steps, summary=summary)

    # Write the rendered HTML to the report file.
    with open(report_filename, 'w') as file:
        file.write(html_content)

# LiteX CI Build/Test ------------------------------------------------------------------------------

def format_name(name):
    return re.sub(r'[^\w-]', '_', name)

def main():
    parser = argparse.ArgumentParser(description="LiteX HW CI")
    parser.add_argument("config_file",                     help="Path to the configurations file.")
    parser.add_argument("--report",                        help="Filename for the HTML report. If not specified, it defaults to the basename of the config file with .html extension.")
    parser.add_argument("--config",                        help="Select specific configuration from file (optional).")
    parser.add_argument("--list", action="store_true",     help="List all available configurations in file and exit.")
    args = parser.parse_args()

    if not args.report:
        base_name = os.path.basename(args.config_file)
        args.report = f"{os.path.splitext(base_name)[0]}.html"

    # Capture the start time.
    test_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Import litex_ci_configs from the specified config file.
    try:
        config_module = __import__(args.config_file.replace(".py", "").replace("/", "."), fromlist=[''])
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

    steps  = ["firmware_build", "gateware_build", "software_build", "setup", "load", "test", "exit"]
    report = {format_name(name): {step.capitalize(): LiteXCIStatus.NOT_RUN for step in steps} for name in litex_ci_configs}

    # Generate empty HTML report.
    os.system("cp html/report.css ./")
    generate_html_report(report, args.report, steps, test_start_time, args.config_file)

    # Iterate on configurations and progressively update report.
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
            report[name]['Time']     = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
            report[name]['Duration'] = f"{duration:.2f} seconds"

            generate_html_report(report, args.report, steps, test_start_time, args.config_file)

    generate_html_report(report, args.report, steps, test_start_time, args.config_file)

if __name__ == "__main__":
    main()

