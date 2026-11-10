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
- **Start the image after the download:** a USB reset is not enough with this bootloader (dfu v1.1);
  send a DFU detach (`bmRequestType 0x21, bRequest 0`) or power-cycle the board without BTN0.
- **Seen 2026-11-10:**
  - Through a YKUSH, `dfu-util` timed out on the first block every time, and `tools/dfu_write.py` froze
    the bootloader at a random block (the LEDs stop on the green "download" pattern). Each freeze
    leaves the gateware partition half-written, and BTN0 is needed at power-on to get the bootloader back.
  - Connected directly to the host, `tools/dfu_write.py 1209 5af1 0 gsd_butterstick.bit` wrote all
    1350 blocks in 7.9 s; `dfu-util` was not retried on that connection.
  - `litedram` PASS over Etherbone (`--uart-name=crossover --with-etherbone`): 256 MiB DDR3 16-bit @
    300 MT/s (CL-6 CWL-5), Memtest OK on 256 MiB, 23.4/29.2 MiB/s write/read (VexRiscv @ 75 MHz).
