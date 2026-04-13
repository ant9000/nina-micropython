from time import sleep
from machine import I2C, Pin

def hexdump(data):
    for i in range(0, len(data), 8):
        print(data[i:i+8].hex(" "))

v_en = Pin(("gpio0", 2), Pin.OUT)
v_en.off()
sleep(.01)
v_en.on()

i2c = I2C("i2c0")
sleep(.01)

ST25DV_ADDR_DATA_I2C = 0xA6 >> 1 # I2C address to be used for ST25DV Data accesses.
ST25DV_ADDR_SYST_I2C = 0xAE >> 1 # I2C address to be used for ST25DV System accesses.

ST25DV_GPO1_REG      = 0x0000
ST25DV_MB_MODE_REG   = 0x000D
ST25DV_LOCKCFG_REG   = 0x000F
ST25DV_ICREF_REG     = 0x0017
ST25DV_UID_REG       = 0x0018
ST25DV_I2CPASSWD_REG = 0x0900

ST25DV_I2C_SSO_DYN_REG = 0x2004
ST25DV_MB_CTRL_DYN_REG = 0x2006
ST25DV_MBLEN_DYN_REG   = 0x2007
ST25DV_MAILBOX_RAM_REG = 0x2008

ST25DV_IS_DYNAMIC_REGISTER = 0x2000

def addr(reg):
    if reg & ST25DV_IS_DYNAMIC_REGISTER:
        return ST25DV_ADDR_DATA_I2C
    return ST25DV_ADDR_SYST_I2C

def read(reg, nbytes):
    return i2c.readfrom_mem(addr(reg), reg, nbytes, addrsize=16)

def write(reg, data):
    return i2c.writeto_mem(addr(reg), reg, data, addrsize=16)

# dump system configuration:
data = read(0x0, 32)
hexdump(data)
print("")

print("IC_REF: ", read(ST25DV_ICREF_REG,1).hex())
print("UID:    ", read(ST25DV_UID_REG,8).hex(':'))

# unlock I2C protected operations (default password is 0)
unlocked = read(ST25DV_I2C_SSO_DYN_REG, 1)[0] & 0x01
if not unlocked:
    i2cpass = bytes([0] * 8)
    write(ST25DV_I2CPASSWD_REG, i2cpass + b'\x09' + i2cpass)
unlocked = read(ST25DV_I2C_SSO_DYN_REG, 1)[0] & 0x01
if not unlocked:
    print("ERROR: not unlocked (wrong password?)")

value = read(ST25DV_LOCKCFG_REG,1)[0]
value = bytes([value | 0x01])
write(ST25DV_LOCKCFG_REG, value)
sleep(.01)
print("LOCKCFG:", read(ST25DV_LOCKCFG_REG, 1).hex())

# enable MB fast transfer mode
value = read(ST25DV_MB_MODE_REG,1)[0]
value = bytes([value | 0x01])
write(ST25DV_MB_MODE_REG, value)
sleep(.01)
print("MB R/W:", read(ST25DV_MB_MODE_REG, 1).hex())

# enable MB
value = read(ST25DV_MB_CTRL_DYN_REG, 1)[0]
value = bytes([value | 0x01])
write(ST25DV_MB_CTRL_DYN_REG, value)
sleep(.01)
print("MB CTRL:", read(ST25DV_MB_CTRL_DYN_REG, 1).hex())

# put message to MB
message = bytes([b for b in range(256)])
write(ST25DV_MAILBOX_RAM_REG, message)
print("MB: wrote", message.hex(':'))
sleep(.01)

# check MB control register
print("MB CTRL:", read(ST25DV_MB_CTRL_DYN_REG, 1).hex())

# read message back from MB
nbytes = read(ST25DV_MBLEN_DYN_REG, 1)[0] + 1
print("MB LEN:", nbytes)
data = read(ST25DV_MAILBOX_RAM_REG, nbytes)
print("MB: read", data.hex(':'))
assert (data == message)

def message_arrived(t):
    print(f"Message arrived: {t}")
    # check MB control register
    print("MB CTRL:", read(ST25DV_MB_CTRL_DYN_REG, 1).hex())
    # read message back from MB
    nbytes = read(ST25DV_MBLEN_DYN_REG, 1)[0] + 1
    print("MB LEN:", nbytes)
    data = read(ST25DV_MAILBOX_RAM_REG, nbytes)
    print("MB: read", data.hex(':'))

gpo = Pin(("gpio0", 13), Pin.IN)
gpo.irq(message_arrived)

# enable GPO, interrupt on RF_PUT_MSG_EN
write(ST25DV_GPO1_REG, b'\x21')
sleep(.01)
print("GPO1:", read(ST25DV_GPO1_REG, 1).hex())

while True:
    sleep(.1)
