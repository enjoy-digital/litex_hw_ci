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
    log_path = Path(log_path)
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

# LiteX CI Config ----------------------------------------------------------------------------------

class LiteXCIConfig:
    def __init__(self, target="",
        gateware_command = "",
        software_command = "",
        setup_command    = "",
        exit_command     = "",
        tty              = "", tty_baudrate=115200,
        test_delay       = 0,
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
        self.test_delay       = test_delay
        self.tests            = tests

    def set_name(self, name=""):
        assert not hasattr(self, "name")
        self.name       = name
        self.output_dir = Path(__file__).parent / f"build_{name}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def perform_step(self, step_name, command, log_filename_suffix, shell=False):
        log_path = self.output_dir / f"{log_filename_suffix}.rpt"
        if execute_command(command, log_path, shell):
            return LiteXCIStatus.SUCCESS
        return getattr(LiteXCIStatus, f"{step_name.upper()}_ERROR")

    def firmware_build(self):
        command = f"python3 -m litex_boards.targets.{self.target} {self.gateware_command} \
        --output-dir={self.output_dir} \
        --soc-json={self.output_dir}/soc.json \
        --build --no-compile-gateware"
        return self.perform_step("build", command, "firmware_build")

    def gateware_build(self):
        command = f"python3 -m litex_boards.targets.{self.target} {self.gateware_command} \
        --output-dir={self.output_dir} \
        --build"
        return self.perform_step("build", command, "gateware_build")

    def software_build(self):
        if self.software_command == "":
            return LiteXCIStatus.NOT_RUN
        r = self.perform_step("build", self.software_command.format(output_dir=self.output_dir), "software_build", shell=True)
        return r

    def setup(self):
        if self.setup_command == "":
            return LiteXCIStatus.NOT_RUN
        r = self.perform_step("setup", self.setup_command, "setup", shell=True)
        return r

    def load(self):
        command = f"python3 -m litex_boards.targets.{self.target} {self.gateware_command} \
        --output-dir={self.output_dir} \
        --load"
        return self.perform_step("load", command, "load")

    def test(self):
        time.sleep(self.test_delay)
        log_path = self.output_dir / f"test.rpt"
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
        r = self.perform_step("exit", self.exit_command, "exit", shell=True)
        return r

# LiteX CI HTML report -----------------------------------------------------------------------------

def enum_to_str(enum_val):
    if enum_val == LiteXCIStatus.NOT_RUN:
        return "-"
    elif isinstance(enum_val, enum.Enum):
        return enum_val.name
    return str(enum_val)

def calculate_total_duration(report):
    total_seconds    = sum(float(results.get('Duration', '0.00 seconds')[:-7]) for results in report.values())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"

def generate_html_report(report, report_filename, steps, start_time, config_file):
    # Prepare data for template.
    for name, results in report.items():
        for step in steps:
            step_key = step.capitalize()
            if step_key in results:
                results[step_key] = enum_to_str(results[step_key])

    # Summary generation.
    tests_executed = sum(1 for results in report.values() if any(status != '-' for status in results.values()))
    total_duration = calculate_total_duration(report)
    summary = f"""
    <strong>Config File:</strong> {config_file}<br>
    <strong>Tests Executed:</strong> {tests_executed}<br>
    <strong>Start Time:</strong> {start_time}<br>
    <strong>Total Duration:</strong> {total_duration}
    """

    # Load and render template.
    env = Environment(loader=FileSystemLoader(searchpath='./'))
    template = env.get_template('html/report_template.html')
    html_content = template.render(report=report, steps=steps, summary=summary)

    # Write to file.
    with open(report_filename, 'w') as file:
        file.write(html_content)

# LiteX CI Build/Test ------------------------------------------------------------------------------

def format_name(name):
    return re.sub(r'[^\w-]', '_', name)

def load_configs(config_file):
    config_module_path = config_file.replace(".py", "").replace("/", ".")
    try:
        config_module = __import__(config_module_path, fromlist=[''])
        return config_module.litex_ci_configs
    except ImportError as e:
        print(f"Error: {e}\nconfigs file '{config_file}' not found or doesn't define 'litex_ci_configs'.")
        return None

def list_configs(configs):
    print("Available configs:")
    for name in configs:
        print(f"- {name}")

def run_config_tests(name, config, report, steps, report_filename, test_start_time, config_file):
    # Format Name.
    name = format_name(name)
    config.set_name(name)

    # Run Config's Steps.
    start_time = time.time()
    for step in steps:
        status = getattr(config, step)()
        report[name][step.capitalize()] = enum_to_str(status)
        update_report_timing(report, name, start_time)
        generate_html_report(report, report_filename, steps, test_start_time, config_file)
        if status not in [LiteXCIStatus.SUCCESS, LiteXCIStatus.NOT_RUN]:
            break

def update_report_timing(report, name, start_time):
    end_time = time.time()
    duration = end_time - start_time
    report[name]['Time']     = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    report[name]['Duration'] = f"{duration:.2f} seconds"

def main():
    parser = argparse.ArgumentParser(description="LiteX HW CI.")
    parser.add_argument("config_file",                       help="Path to the configs file.")
    parser.add_argument("--report",                          help="Filename for the HTML report, defaults to basename of the config file with .html extension.")
    parser.add_argument("--config",                          help="Select specific config from file (optional).")
    parser.add_argument("--list",       action="store_true", help="List all available configs in file and exit.")
    parser.add_argument("--test-only",  action="store_true", help="Run tests without compiling firmware, gateware, or software. Assumes necessary binaries are already available.")
    args = parser.parse_args()

    # Set HTML Report File.
    args.report = args.report or f"{Path(args.config_file).stem}.html"

    # Get Start Time.
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Load Configs.
    litex_ci_configs = load_configs(args.config_file)
    if litex_ci_configs is None:
        return

    # List Configs (Optional).
    if args.list:
        list_configs(litex_ci_configs)
        return

    # Select Config (Optional).
    selected_config = args.config
    if selected_config and selected_config not in litex_ci_configs:
        print(f"Error: config '{selected_config}' not found.")
        return

    # Define Steps.
    steps = [
        "firmware_build",
        "gateware_build",
        "software_build",
        "setup",
        "load",
        "test",
        "exit",
    ]
    # When --test-only, skip compilation steps.
    if args.test_only:
        compile_steps = ["firmware_build", "gateware_build", "software_build"]
        steps = [step for step in steps if step not in compile_steps]

    # Initialize Report.
    report = {format_name(name): {step.capitalize(): LiteXCIStatus.NOT_RUN for step in steps} for name in litex_ci_configs}
    os.system("cp html/report.css ./")
    generate_html_report(report, args.report, steps, start_time, args.config_file)

    # Run Configs.
    for name, config in litex_ci_configs.items():
        if selected_config and name != selected_config:
            continue
        run_config_tests(name, config, report, steps, args.report, start_time, args.config_file)

    # Finish Report.
    generate_html_report(report, args.report, steps, start_time, args.config_file)

if __name__ == "__main__":
    main()
