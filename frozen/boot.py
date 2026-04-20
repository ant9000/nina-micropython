from time import sleep_ms, time_ns
from st25dv import ST25DV
from thyrakey import *

def hexdump(data):
    for i in range(0, len(data), 8):
        print(data[i:i+8].hex(" "))

challenge = None
start = None
def message_arrived(nfc, data):
    global challenge, start
    _start = time_ns()
    if start and _start - start > 3000000000:
        # expire timed out challenge
        challenge = start = None
    print("Message arrived")
    signed = SignedMessage.from_data(data)
    if signed.is_valid():
        print(f"Payload: {signed.payload.hex()}")
        if challenge is None:
            start = _start
            challenge = Challenge(door.key, door.pubkey, signed.pubkey)
            print(f"Challenge seed: {challenge.seed.hex()}")
            answer = challenge.data
            nfc.mailbox_put(answer)
            print(f"Challenge sent")
        else:
            if challenge.is_valid(signed.data):
                elapsed = (time_ns() - start) / 1000000
                print(f"Peer authenticated in {elapsed} ms")
            else:
                print("ERROR: peer authentication failed")
            challenge = None
            start = None
    else:
        print("ERROR: message is not signed")
        challenge = None

door = Door()

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
