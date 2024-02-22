[> Status
----------

* buildroot version: master (must moved to a release)
* Linux: 6.4.9 (fails to boot early versions).
* openSBI: TBD

### CPUs

* vexriscv_smp: ok (`litex_vexriscv_defconfig` and `litex_vexriscv_usbhost_defconfig` with `--with-usb`)
* naxriscv 32 : TBD
* naxriscv 64 : won't boot (nothing after openSBI)

Currently only tested with digilent arty target.

[> Details
----------

A boot script is executed as the latest init script. It check:

* network configuration/access
* scard support (currently only spi-sdcard support): a /dev node is
 present/not present, a partition is mountable or not, and if it's
 possible to read file's content
* USB host support: similar to sdcard support: a mass storage must be plugged to the USB port, with a fat partition and a file.

USB support is a enabled by default option: `--with-usb` must be added to `make.py`

## Network test

The target must be connected by an RJ45 cable to a PC. If PC's IP address is
diferent than *192.168.1.100*, argument `--remote-ip` must be used at build
time.

Sequence:
* `ìfconfig` is used to check if the interface is ready;
* *gateway* IP is obtained from `route`command;
* `ping` return code is evaluated to validate/unvalidate ability to access others machine.

If all steps are successfully executed the message:
```
Network Test: OK
```
is displayed or
```
Network Test: KO
```
otherwise.

## SDCARD test

A digilent pmod sd is plugged to *PMOD D*, a card must be inserted, with a file
called **litex_ci.txt** containing the text **Hello World** located in the first
partition (fat format).

If the script is able to find **/dev/mmcblk0p1**, to mount partition and to read the file's content the message:

```
MMC Test: OK
```
will be displayed or
```
MMC Test: KO
```
if one of the steps fails

## USB test

A *Machdyne PMOD dual USB* must be connected to *PMOD A*, an USB key  (or any mass storage device) must be
plugged to the top connector, with a file called **litex_ci.txt** containing the
text **Hello World** located in the first fat partition.

If the script is able to find **/dev/sda1**, to mount partition and to read the file's content the message:

```
USB Test: OK
```
will be displayed or
```
USB Test: KO
```
if one of the steps fails.