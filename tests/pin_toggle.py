from machine import Pin
from time import sleep

p = Pin(("gpio0", 2), Pin.OUT)

state = 0
while True:
    p(state)
    state = 1 - state
    sleep(1)