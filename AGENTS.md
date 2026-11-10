# LiteX HW CI for agents

This repo describes **what** to test on LiteX hardware. It never says **where** a board is: machines,
IP addresses, USB hub ports and serial ports belong to each lab's own inventory, outside this repo.
An agent (or a person) combines the two.

## Layout
- `suites/<suite>.md`: one test pack per feature (`bios`, `litedram`, `liteeth`, ...). Each one gives the
  intent, the build options it needs, the steps, and the pass/fail criteria.
- `boards/<litex-boards target>.md`: per-board hints: build arguments, how to load, how to reach the
  console, and known quirks. Most details come from litex-boards itself; only what the target
  file does not tell you goes here.
- `tools/`: small helpers with no lab knowledge: `ykush.py` (YKUSH hub ports over pyusb),
  `dfu_load.sh` (load through a DFU bootloader with dfu-util and reset), `dfu_write.py` (pyusb DFU
  writer that checks the status after each block, for bootloaders where dfu-util fails).
- `litex_hw_ci.py`, `configs/`, `linux/`, `nuttx/`: the 2024 runner and its configs (Linux and NuttX
  boots on several CPUs). Still usable; new tests go in `suites/` and `boards/`.

## How a run goes
1. Read the suite and the board hint, then the lab inventory for where the board is.
2. Build with `python3 -m litex_boards.targets.<target> <suite and board args> --build`. Build on a
   fast machine and copy the bitstream to the test host if they differ.
3. Power only the board under test (`tools/ykush.py down a; tools/ykush.py up N`), then load it.
4. Drive the console with `litex_term` scripted mode, which needs no TTY:
   `python3 -m litex.tools.litex_term PORT --send "CMD" --expect "REGEX" --timeout S --json`
   (`PORT` is a tty, `crossover` with a running `litex_server`, or `jtag`). `--expect` is one regex
   applied after **every** `--send` (default `litex>`): keep the default and judge the output, or run
   one `litex_term` call per check. With `crossover`, give `litex_server --bind-port` and
   `litex_term --crossover-port` a free port: 1234 may already be used by another session's tunnel.
5. Judge the output against the suite's pass criteria, and report the versions (litex, litedram,
   litex-boards commits), the measured numbers and the result.
6. Power the hub ports down.

If something does not match (device missing, wrong IDs, load does not start the image), investigate
and record what you found in the board hint or the lab inventory, instead of retrying blindly.

## Rules
- Never write a board's bootloader or factory flash area. DFU bootloaders only write the user image.
- Check the target's IDs before loading (USB VID:PID, JTAG IDCODE): two boards can share an ID.
- Leave the bench as you found it: hub ports off, no server left running.
