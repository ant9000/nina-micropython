from time import sleep_ms
from st25dv import ST25DV
from thyrakey import *

def hexdump(data):
    for i in range(0, len(data), 8):
        print(data[i:i+8].hex(" "))

door = Door(debug=True)

def message_arrived(nfc, data):
    print(f"Message arrived: {data.hex()}")
    answer = door.process_data(data)
    if answer is not None:
        nfc.mailbox_put(answer)
        print(f"Sent answer: {answer.hex()}")

nfc = ST25DV(
    i2c_dev="i2c0",
    enable_pin=("gpio0", 2),
    irq_pin=("gpio0", 13),
    on_message_cb=message_arrived
)

print("UID:", nfc.read_mem(ST25DV.UID_REG,8).hex(':'))
print("Waiting for peers...\n")

while True:
    sleep_ms(10)
