from time import sleep
from st25dv import ST25DV

def hexdump(data):
    for i in range(0, len(data), 8):
        print(data[i:i+8].hex(" "))

def message_arrived(nfc, data):
    print(f"Message arrived: {data.hex()}")
    reversed = bytes([data[i-1] for i in range(len(data),0,-1)])
    nfc.mailbox_put(reversed)
    print(f"Message sent: {reversed.hex()}")

nfc = ST25DV(
    i2c_dev="i2c0",
    enable_pin=("gpio0", 2),
    irq_pin=("gpio0", 13),
    on_message_cb=message_arrived
)

# dump system configuration:
data = nfc.read_mem(0x0, 32)
hexdump(data)
print("")
print("UID:", nfc.read_mem(ST25DV.UID_REG,8).hex(':'))

while True:
    sleep(.1)
