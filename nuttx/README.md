# LiteX NuttX Build Status and Testing Procedures

[> Overview
-----------

This document outlines the current status of LiteX NuttX builds and provides a guide to testing hardware compatibility.

### Software Versions

- **NuttX / NuttX-Apps Version**: Master branch.
- **NuttX Defconfig**: **netnsh**.

### CPU Compatibility

- **vexriscv 32 secure**: Pass.

Testing has been performed on the Digilent on the Digilent Arty A7-35T and A7-100T platforms.

[> Prerequisites
----------------

Installation of necessary tools:

```
apt install kconfig-frontends
```

For further details, refer to the [NuttX Quick Start Guide](https://nuttx.apache.org/docs/latest/quickstart/install.html).


[> Testing Procedures
---------------------

Currently, testing focuses on *liteuart* and *liteeth* modules. The *litesd* module appears to be non-functional due to incorrect configuration.

### UART Testing Procedure

The UART interface should be set to a baud rate of 1000000 (1M). While 115200 baud may work, it can result in character loss.

**Success Criteria**: The presence of the `NuttShell (NSH)` sequence indicates a successful test.

### Ethernet Testing Procedure

Perform the following sequences:
- **Configuration**: Use `ifconfig LOCAL_IP` to set up the *eth0* interface with an IP address provided by *config_nuttx.py*. This step doesn't involve reading back the configuration.
- **Connectivity Test**: Execute `ping REMOTE_IP` to test if NuttX can ping the host computer. A successful test requires finding the phrase `10 packets transmitted, 10 received, 0% packet loss` in NuttX's response.

[> Notes and Limitations
------------------------

- The *memorymap* configuration is hardcoded in `arch/risc-v/src/litex/hardware/litex_memorymap.h`. Customization is possible by specifying `CONFIG_LITEX_CUSTOM_MEMORY_MAP_PATH`.
- Similarly, IRQ configuration can be customized through `LITEX_CUSTOM_IRQ_DEFINITIONS_PATH`.
- The `sys_clk_freq` parameter is set to 100MHz in the default configuration but can be adjusted via `make menuconfig`.
- Is there a method to generate custom IRQ, memory map, and defconfig files efficiently?
