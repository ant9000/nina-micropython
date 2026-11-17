from time import sleep_ms
from st25dv import ST25DV
from thyrakey import *
from pins import *
from rgb import RGB
from machine import Pin
import time

def hexdump(data):
    for i in range(0, len(data), 8):
        print(data[i:i+8].hex(" "))

rgb = RGB(RGB_PIN)
lock = Pin(DOOR_LOCK, Pin.OUT)

def message_arrived(nfc, data):
    rgb.blue()
    print(f"Message arrived: {data.hex()}")
    answer = door.process_data(data)
    if answer is not None:
        nfc.mailbox_put(answer)
        print(f"Sent answer: {answer.hex()}")
    rgb.off()

def unlock_door():
    lock(1)
    time.sleep(1)
    lock(0)

nfc = ST25DV(
    i2c_dev="i2c0",
    lpd_pin=NFC_LPD,
    gpo_pin=NFC_GPO,
    on_message_cb=message_arrived
)
uid = nfc.read_mem(ST25DV.UID_REG,8)
door = Door(uid, unlock_door, debug=True)

print("UID:", door.uid.hex(':'))
print("PUBKey:", door.pubkey.hex(':'))
print("Owners:")
for owner in door.owners:
    print("\t", owner.hex(':'))
print("Waiting for peers...\n")

while True:
    sleep_ms(10)
