# Nuttx on LiteX

## Install

### Env

- `apt install kconfig-frontends`
- must have a riscv toolchain (debian's riscv64-unknown seems not working (missing math.h). sifive's toolchain is fine.)

### Nuttx

```
#create the workspace
mkdir somewhere/nuttxOnLiteX

cd somewhere/nuttxOnLiteX

# Clone nuttx.
git clone https://github.com/apache/nuttx.git nuttx

# Clone apps (warning: must be called apps to respect default path).
git clone https://github.com/apache/nuttx-apps apps
```

**Note**
For titanium board patch *nuttx_on_titanium.patch* must be applied (different phy).

## Nuttx: Init/config/compile

```
cd nuttx
./tools/configure.sh -l arty_a7:netnsh
```

**Note:** `nsh` is the basic configuration, `netnsh` is the basic configuration with network support. See **boards/risc-v/litex/arty_a7/configs**.

### Tweak


```
make menuconfig
```

To change default IP ADDR (IP is a 32bits hex format)

```
Application Configuration
 |
 +--> Network Utilites
       |
       +--> Network Initialization
             |
             +--> IP Address Configuration
                   |
                   +--> Target IPv4 address (NETINIT_IPADDR)
                   |
                   +--> Router IPv4 address (NETINIT_DRIPADDR)
```

### Build

```
make -j
```

### install for netboot

```
cd nuttx.bin /tftpboot/boot.bin
```

## LiteX

```
python -m digilent_arty.py --with-ethernet --with-sdcard --cpu-type=vexriscv --cpu-variant=secure --uart-baudrate 1000000 --build --load
```

## Tests

```
litex_term --speed 1000000 /dev/ttyUSB1
```

### Ping/network
```
nsh> ifconfig eth0 192.168.1.50
nsh> ping 192.168.1.4
```

## Refs

- https://nuttx.apache.org/docs/latest/quickstart/install.html
- https://nuttx.apache.org/docs/latest/platforms/risc-v/litex/index.html
