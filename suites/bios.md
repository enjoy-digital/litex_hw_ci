# Suite: bios

**Intent:** the SoC boots and the LiteX BIOS console answers.

**Build:** the board's default target (no extra arguments).

**Steps (BIOS console):**
1. `ident`: expect `Ident:`.
2. `help`: expect `LiteX BIOS, available commands`.

**Pass:** both expectations are met within 5 s each.

**Report:** the LiteX git sha1 printed by `ident` or the boot banner, the CPU and its frequency.
