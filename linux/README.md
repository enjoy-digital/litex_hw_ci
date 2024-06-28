# LiteX HW CI Linux Build Status and Testing Guide

[> Overview
-----------

This document outlines the current status of LiteX Linux builds and provides a guide to testing hardware compatibility.

### Software Versions

- **Buildroot**: Currently using the master branch. Transition to a specific stable release is recommended.
- **Linux Kernel**: Version 6.4.9. (Earlier versions fail to boot which will be investigated).
- **OpenSBI**: Version 1.3.1. This version is specific to LiteX and can be found in the litex-hub/opensbi repository, branch 1.3.1-linux-on-litex-vexriscv.

### CPU Compatibility

- **vexriscv_smp**: Fully supported.
- **naxriscv 32-bit**: Fully supported.
- **naxriscv 64-bit**: Fully supported.
- **Rocket CPU**: Fully supported.

Testing has been performed on the Digilent Arty platform and the LiteX Acorn Baseboard mini.

[> Testing Procedures
---------------------
The final initialization script of the boot process includes a series of tests to verify:

- **Network Configuration/Access**: Confirms the system's ability to connect to a network.
- **SD Card Support**: Tests for SPI SD card support, checking for the presence of a `/dev` node, mountability of a partition, and readability of file contents.
- **USB Host Support**: Similar to SD card testing but focuses but with a USB Key.

### Network Connectivity Test

1. Connect the target device to a PC using an RJ45 cable. If the PC's IP address is not *192.168.1.100*, specify a different address using the `--remote-ip` argument during build.
2. Validate the network interface's readiness with `ifconfig`.
3. Use the `route` command to identify the gateway IP address.
4. Perform a `ping` test to confirm connectivity to other machines.

**Results**:
- `Network Test: OK` indicates successful connectivity.
- `Network Test: KO` signals a failure.

### SD Card Functionality Test

Insert an SD card containing a file named **litex_ci.txt** with the content **Hello World** into a Digilent PMOD SD connected to *PMOD D*.

**Results**:
- `MMC Test: OK` indicates that detecting **/dev/mmcblk0p1**, mounting the partition, and reading the file's content yields has been successful .
- `MMC Test: KO` signals a failure.

### USB Device Functionality Test

Attach a Machdyne PMOD dual USB to *PMOD A* and connect a USB storage device with a FAT partition containing **litex_ci.txt** with **Hello World**.

**Results**:
- `USB Test: OK` indicates that detecting **/dev/sda1**, mounting the partition, and reading the file's content yields has been successful .
- `USB Test: KO` signals a failure.
