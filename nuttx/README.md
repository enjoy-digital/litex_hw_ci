[> Status
---------

* nuttx / nuttx-apps version: master
* nuttx defconfig: **netnsh**

### CPUs

* vexriscv 32 secure: ok
* vexriscv 32 smp: TDB

Currently only tested with digilent arty 35t/100t target.

[> Prerequisites
-----------------

`apt install kconfig-frontends`

Ref: https://nuttx.apache.org/docs/latest/quickstart/install.html

[> Details
----------

Only *liteuart* and *liteeth* are tested (litesd seems not working / bad
configuration).

## UART test

UART must be configured with a 1000000 baudrate (115200 works but seems to lost
chars).

This test check if sequence `NuttShell (NSH)` is displayed

## Ethernet test

Two sequences are sent:
* `ifconfig LOCAL_IP` to configure *eth0* interface with ip provided by the
  *config_nuttx.py*. No read is done
* `ping REMOTE_IP` to verify if nuttx is able to ping host computer. The sequence
  `10 packets transmitted, 10 received, 0% packet loss` must be find in nuttx
  answer

[> Notes and limitations
------------------------

* *memorymap* is hardcoded in *arch/risc-v/src/litex/hardware/litex_memorymap.h* but it
  seems possible to provides another file by using
  `CONFIG_LITEX_CUSTOM_MEMORY_MAP_PATH`. It's also true for IRQ with
  `LITEX_CUSTOM_IRQ_DEFINITIONS_PATH`
* *sys_clk_freq* is fixed in `defconfig` at 100MHz but may be modified using
  `make menuconfig`
* A solution to generate custom *irq*, *memorymap* and *defconfig* ?
