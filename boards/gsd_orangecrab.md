# Board: gsd_orangecrab (OrangeCrab r0.2)

- **Build:** `--without-dfu-rst`. Without it, the image can jump back to the DFU bootloader about 2 s
  after boot (the reset-to-bootloader logic sees the user button as pressed). Check the ECP5 size on
  the chip: the default is `--device=25F`; an image for the wrong size does not start.
- **Load:** DFU bootloader (foboot, `1209:5af0`, alt 0): `tools/dfu_load.sh 1209 5af0 gsd_orangecrab.bit 0`.
  The board enters the bootloader at power-on, so power-cycle it first if it is running an image.
  `openFPGALoader --dfu` writes the image but does not reset the board, so the image does not start;
  use `dfu-util -R` (what `dfu_load.sh` does).
- **Run only on demand:** at power-on the board stays in the DFU bootloader even with a valid image
  in flash (seen 2026-11-10, foboot v3.1), so it never runs anything by itself. To start the stored
  image without reloading it: `dfu-util -d 1209:5af0 -a 0 -e` (it prints "can't detach", then resets
  the board and the image starts, `/dev/ttyACM0` within 2 s). A power cycle returns to DFU.
- **Console:** LiteX `usb_acm` UART (`1209:0001`, `/dev/ttyACM*`) about 3 s after the load. The boot log
  is printed before the port can be opened, so drive the BIOS with commands rather than waiting for
  the banner.
- **Seen:** 2026-11-10, r0.2 25F, `litedram` PASS (128 MiB DDR3 @ 192 MT/s, Memtest OK on 128 MiB).
