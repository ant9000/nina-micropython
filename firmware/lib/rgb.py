"""Driver WS2812 e colori di stato"""
from machine import SPI
from ws2812 import WS2812

class RGB:
    def __init__(self):
        self.led = WS2812(spi=SPI("spi1"))

    def color(self, r, g, b):
        self.led.show([(r & 0xFF, g & 0xFF, b & 0xFF)])

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
