import time
from machine import Pin, bitstream

p = Pin(('gpio0', 25), Pin.OUT)

MULT = 1
# --- Timing in ns: (T0H, T0L, T1H, T1L) ---
TIMINGS_BASE = (400, 850, 800, 450)
timings = [t*MULT for t in TIMINGS_BASE]
BUF = b'\x00\xff\x00\xff\x00\x00\x00\x00\xff'*2
 
while True:
    bitstream(p, 0, timings, BUF)
    time.sleep_ms(6)

