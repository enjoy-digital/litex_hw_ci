# Board: litex_acorn_baseboard_mini (LiteX Acorn Baseboard Mini + SQRL Acorn CLE-215+)

- **Build:** the default variant is `cle-215+` (xc7a200t-fbg484-3); `--variant=cle-215` or `cle-101`
  for the other modules. Vivado is needed.
- **Load:** JTAG through the baseboard FTDI chip, with openFPGALoader (the litex-boards target
  defaults to OpenOCD: pass `--programmer=openfpgaloader`). The chip
  depends on the baseboard release: FT2232 (`0403:6010`) or FT4232 (`0403:6011`) on newer
  releases, and the openFPGALoader cable must match it (`ft2232`, `ft4232`; `digilent_hs2` for an
  FT232H, `0403:6014`). Detect it, don't assume it. `openFPGALoader --detect` should report an
  xc7a200t. `--load` writes the SRAM (lost at power-off), which is what a run needs: do not write
  the SPI flash unless asked.
- **Several boards on one host:** the FTDI chip has no USB serial number, so boards of the same
  release have the same IDs, and the platform's `detect_ftdi_chip()` uses the first chip `lsusb`
  lists, which may be another board's. Select a board by the **host USB port** it is plugged into
  (stable), and detect the chip and the bus/device numbers (they change on each replug) of that port:
  ```sh
  p=/sys/bus/usb/devices/1-3   # Host USB port of the board, see the lab inventory.
  case "$(cat $p/idVendor):$(cat $p/idProduct)" in
    0403:6010) cable=ft2232;; 0403:6011) cable=ft4232;; 0403:6014) cable=digilent_hs2;;
    *) echo "no supported FTDI chip on $p"; exit 1;;
  esac
  openFPGALoader --cable $cable --busdev-num $(cat $p/busnum):$(cat $p/devnum) <bitstream>.bit
  ```
  List the boards and their chips with
  `for d in /sys/bus/usb/devices/*; do case "$(cat $d/idVendor 2>/dev/null):$(cat $d/idProduct 2>/dev/null)" in 0403:6010|0403:6011|0403:6014) echo "$(basename $d) $(cat $d/idProduct)";; esac; done`.
- **Console:** 115200 baud, on one of the FTDI chip's interfaces: interface `1.1` on an FT2232
  baseboard (seen 2026-11-11). An FT4232 has four interfaces: check which one answers before relying
  on it. Use the stable name that only depends on the host USB port:
  `/dev/serial/by-path/<controller>-usb-0:<port>:<interface>-port0` (`ls -l /dev/serial/by-path`).
  The baseboard routes it to FPGA pins G1 (TX) / Y13 (RX), from the litex-boards
  `litex_acorn_baseboard_mini` extension. A design built on the bare `sqrl_acorn` platform puts
  `serial` on the Acorn P2 header instead and is unreachable: add the extension first
  (`platform.add_extension(sqrl_acorn.litex_acorn_baseboard_mini, prepend=True)`).
- **Transceivers (GTP, one quad):**
  - SFP0: TX D5/C5, RX D11/C11. SFP1: TX B4/A4, RX B8/A8. PCIe lane 0 (B6/B10) goes to the SATA
    connector, lane 3 (D7/D9) to the PCIe x1 edge.
  - No MGTREFCLK reaches the SFP lanes: the GTP QPLL takes its reference from a fabric PLL on the
    200 MHz oscillator (`GTGREFCLK`, DRC REQP-49 downgraded to a warning, as in the litex-boards
    target). 1.25 to 3.125 Gbps are comfortable; check 5 Gbps with a PRBS test first.
  - P/N swaps: TX polarity 0 and RX polarity 1 on both SFPs (RX inverted on the Acorn, TX inverted on
    the Acorn and on the baseboard). SFP1 checked on two boards, 2026-11-11 (see below).
  - LEDs are on the Acorn module (`user_led` 0-3).
- **SerDes design for the `serdes_link` suite:** none upstream covers the SFP ports yet. The suite
  needs a LiteICLink `GTP` on each SFP with a link layer above it (e.g. SerWB, one SFP as initiator
  and the other as target, so that one gateware fits every board and every DAC cable joins an SFP0
  to an SFP1). LiteICLink's `bench/serdes/sqrl_acorn.py` only exercises the GTP on PCIe lane 0 (the
  SATA connector here) and needs the baseboard extension above for its UART; its
  `bench/serdes/test_prbs.py` can run step 5 of the suite.
- **Seen 2026-11-11** (LiteICLink GTP + SerWB design as above, two boards, two passive DAC cables
  A.SFP0-B.SFP1 and B.SFP0-A.SFP1, 2.5 Gbps, sys 100 MHz, Vivado 2023.2, timing met, WNS 0.704 ns):
  - PRBS31 10 s, 4 directions: 0 errors (BER < 4e-11).
  - Remote register access over SerWB (burst depth 64): writes 192.5 MB/s, reads 4.65 MB/s per
    cable, 0 errors.
