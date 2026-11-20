from time import sleep_ms
from rgb import RGB

led = RGB()

try:
    while True:
        for c in range(0,256,5):
            led.color(c, 0, 0)
            sleep_ms(15)
            
        for c in range(255,0,-5):
            led.color(c, 0, 0)
            sleep_ms(15)
except KeyboardInterrupt:
    pass

led.off()