"""Driver WS2812 e colori di stato"""
import time
from machine import Pin, bitstream

class RGB:
    _TIMING = (250, 900, 900, 250)

    def __init__(self, pin):
        self.pin = Pin(pin, Pin.OUT)

    def color(self, r, g, b):
        data = bytes([g & 0xFF, r & 0xFF, b & 0xFF])
        bitstream(self.pin, 0, self._TIMING, data)
        time.sleep_us(80)

    def red(self, level=255):
        self.color(level, 0, 0)

    def green(self, level=255):
        self.color(0, level, 0)

    def blue(self, level=255):
        self.color(0, 0, level)

    def yellow(self, level=255):
        self.color(level, level, 0)

    def magenta(self, level=255):
        self.color(level, 0, level)

    def white(self, level=255):
        self.color(level, level, level)

    def off(self):
        self.color(0, 0, 0)
