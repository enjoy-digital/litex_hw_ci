# Suite: litedram

**Intent:** the DRAM initialises, calibrates and holds data over its full size.

**Build:** the board's default target, with its default SDRAM module (or the one given in the board
hint).

**Steps (BIOS console):**
1. `mem_list`: read the `MAIN_RAM` origin and size.
2. `sdram_init`: re-runs initialisation and calibration and prints the leveling results and a short
   `Memtest`. Expect `Memtest OK`.
3. `mem_test <origin> <size>` over the full `MAIN_RAM`: expect `Memtest OK`. Use a long timeout
   (60 s or more): it is CPU-bound.
4. `mem_speed <origin> 0x1000000`: read the write and read speeds.

**Pass:** `Memtest OK` at steps 2 and 3, and no `Memtest KO` or error count.

**Report:** the SDRAM line of the boot banner (size, width, rate, CL/CWL), the leveling result of each
module (window width), the full-size memtest result and the speeds. The speeds are limited by the
CPU, so compare them only with earlier runs of the same build; flag a drop of more than 30%.
