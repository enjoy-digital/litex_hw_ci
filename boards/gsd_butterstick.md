# Board: gsd_butterstick (ButterStick r1.0)

- **Build:** the default target uses the `crossover` UART, so the console needs Etherbone:
  `--uart-name=crossover --with-etherbone --eth-ip=<free IP on the lab network>` (default IP
  192.168.1.50, which may be inside a DHCP range: pick one that is free).
- **Load:** without an external JTAG adapter (FT232H, `0403:6014`), use the DFU bootloader
  (`1209:5af1`): `tools/dfu_load.sh 1209 5af1 gsd_butterstick.bit 0`.
  - Flash partitions in the [bootloader source](https://github.com/butterstick-fpga/butterstick-bootloader)
    (`firmware/main.c`): alt 0 = gateware @0x200000, alt 1 = firmware, alt 2 = extra. The bootloader
    partition (0x0) is only exposed after holding BTN0 for 5 s, and the bootloader write-protects it.
  - The alt names read over USB can be shifted by one string index (seen 2026-11-10: alt 1 showed
    as "flash @0x200000 (gateware)"). Trust the source, not the names.
  - A running LiteX image exposes a DFU *runtime* interface; `dfu-util` detaches it into the bootloader.
- **Boot:** at power-on the bootloader jumps straight to the gateware at 0x200000 unless BTN0 is held
  or a magic word is in security register 3. If that partition is erased or invalid, the board shows
  nothing on USB: **hold BTN0 while powering it** to get the DFU bootloader back, then reload.
- **Seen:** 2026-11-10, a first DFU download stopped with `LIBUSB_ERROR_TIMEOUT` after 512 bytes and the
  bootloader stopped answering (it erases flash synchronously inside the USB callback). The partially
  erased gateware then did not boot after a power cycle. Recovery needs BTN0 (physical access).
  > TODO: find why the first block timed out.
