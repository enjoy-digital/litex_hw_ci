# Suite: serdes_link

**Intent:** a transceiver link between two SoCs (or two ports of one board) comes up, carries data
without errors, and survives a cable unplug: physical layer (PRBS), link layer, remote register
access and, if built, streaming.

**Boards:** one board with a cable between two of its transceiver ports, or two boards cabled
together. Unlike the other suites, **both ends must be powered at the same time** (two hub ports up
for two boards).

**Build:** the board's SerDes design given in the board hint, with the same options on both ends of
a cable (line rate, CRC, stream port). Report the line rate and the timing summary.

**Steps (host, through `litex_server`, one per board):**
1. Ident: each board answers with its SerDes design identifier.
2. Polarity: each receiver gets valid link idles, with its default RX polarity or after swapping it.
   Report any polarity that differs from the board hint.
3. Wiring: find which port is connected to which (silence each TX in turn). Every cable must receive
   in both directions.
4. Status: transceivers ready, TX/RX clocks at line rate / datapath width (±0.05%), link ready, 0 RX
   errors, 0 link drops.
5. PRBS31 on every direction for at least 10 s (300 s for a release): count bit errors.
6. Remote access: read the remote identifier through the link, then write and read back 256 random
   words in a remote memory, and check them directly on the remote board.
7. Bandwidth: write, read (and read with prefetch, if available) throughput of the remote access.
8. Stream (if built): every direction at full speed, then with a slow consumer; count data errors,
   frame errors and RX overflows.
9. Final status: the counters of step 4 are still 0.
10. Robustness (optional): unplug a cable and plug it back: the link comes back, the link drop
    counter increases by one, and steps 6 and 8 pass again.

**Pass:** steps 1 to 9 pass: 0 PRBS errors, 0 data or frame errors, 0 overflows, identifiers match,
and the counters stay at 0. Throughput is not a pass criterion.

**Report:** the cabling (which port to which), the polarities, the line rate, the PRBS duration and
BER bound per direction, the throughput figures, and the commits of the design, LiteX and
LiteICLink. Compare throughput only with earlier runs of the same build and line rate; flag a drop
of more than 10%.
