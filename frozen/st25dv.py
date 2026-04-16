from time import sleep
from machine import I2C, Pin

class ST25DV:
    ADDR_DATA_I2C = 0xA6 >> 1 # I2C address to be used for ST25DV Data accesses.
    ADDR_SYST_I2C = 0xAE >> 1 # I2C address to be used for ST25DV System accesses.

    GPO1_REG      = 0x0000
    MB_MODE_REG   = 0x000D
    LOCKCFG_REG   = 0x000F
    ICREF_REG     = 0x0017
    UID_REG       = 0x0018
    I2CPASSWD_REG = 0x0900

    I2C_SSO_DYN_REG = 0x2004
    MB_CTRL_DYN_REG = 0x2006
    MBLEN_DYN_REG   = 0x2007
    MAILBOX_RAM_REG = 0x2008

    IS_DYNAMIC_REGISTER = 0x2000

    def __init__(self, i2c_dev, enable_pin, irq_pin, on_message_cb=None, i2c_pass=None):
        self.i2c_dev = I2C(i2c_dev)
        self.enable_pin = Pin(enable_pin, Pin.OUT)
        self.irq_pin = Pin(irq_pin, Pin.IN)
        self.on_message_cb = on_message_cb
        self.i2c_pass = i2c_pass or bytes([0] * 8)
        self.reset()
        assert self.is_present(), "not found"
        assert self.unlock(), "not unlocked"
        assert self.lock_rf_config(), "RF config not locked"
        assert self.enable_mb_transfer_mode(), "MB transfer not enabled"
        assert self.enable_mb(), "MB not enabled"
        self.irq_pin.irq(lambda pin: self.on_gpo())
        assert self.configure_gpo(), "GPO not configured"

    def _addr(self, reg):
        if reg & ST25DV.IS_DYNAMIC_REGISTER:
            return ST25DV.ADDR_DATA_I2C
        return ST25DV.ADDR_SYST_I2C

    def read_mem(self, reg, nbytes):
        return self.i2c_dev.readfrom_mem(self._addr(reg), reg, nbytes, addrsize=16)

    def write_mem(self, reg, data):
        return self.i2c_dev.writeto_mem(self._addr(reg), reg, data, addrsize=16)

    def reset(self):
        self.enable_pin.off()
        sleep(.01)
        self.enable_pin.on()
        sleep(.01)

    def is_present(self):
        return self.read_mem(ST25DV.ICREF_REG,1)[0] == 0x51

    def unlock(self):
        unlocked = self.read_mem(ST25DV.I2C_SSO_DYN_REG, 1)[0] & 0x01
        if not unlocked:
            self.write_mem(ST25DV.I2CPASSWD_REG, self.i2c_pass + b'\x09' + self.i2c_pass)
            sleep(.01)
            unlocked = self.read_mem(ST25DV.I2C_SSO_DYN_REG, 1)[0] & 0x01
        return unlocked

    def lock_rf_config(self):
        value = self.read_mem(ST25DV.LOCKCFG_REG,1)[0]
        value = bytes([value | 0x01])
        self.write_mem(ST25DV.LOCKCFG_REG, value)
        sleep(.01)
        return self.read_mem(ST25DV.LOCKCFG_REG,1)[0] & 0x01

    def enable_mb_transfer_mode(self):
        value = self.read_mem(ST25DV.MB_MODE_REG,1)[0]
        value = bytes([value | 0x01])
        self.write_mem(ST25DV.MB_MODE_REG, value)
        sleep(.01)
        return self.read_mem(ST25DV.MB_MODE_REG, 1)[0] & 0x01

    def enable_mb(self):
        value = self.read_mem(ST25DV.MB_CTRL_DYN_REG, 1)[0]
        value = bytes([value | 0x01])
        self.write_mem(ST25DV.MB_CTRL_DYN_REG, value)
        sleep(.01)
        return self.read_mem(ST25DV.MB_CTRL_DYN_REG, 1)[0] & 0x01

    def configure_gpo(self):
        # enable GPO, interrupt only on RF_PUT_MSG_EN
        self.write_mem(ST25DV.GPO1_REG, b'\x21')
        sleep(.01)
        return self.read_mem(ST25DV.GPO1_REG, 1)[0] == 0x21

    def on_gpo(self):
        message = self.mailbox_get()
        if message and self.on_message_cb:
            self.on_message_cb(self, message)

    def mailbox_get(self, only_rf=True):
        if only_rf: # check MB control register
            value = None
            while value is None:
                try:
                    value = self.read_mem(ST25DV.MB_CTRL_DYN_REG, 1)[0]
                except OSError:
                    pass
            if value & 0x80 != 0x80:
                return
        nbytes = self.read_mem(ST25DV.MBLEN_DYN_REG, 1)[0]
        if nbytes:
            message = self.read_mem(ST25DV.MAILBOX_RAM_REG, nbytes+1)
            return message

    def mailbox_put(self, message):
        assert len(message) < 255, "Message too long"
        self.write_mem(ST25DV.MAILBOX_RAM_REG, message)
        sleep(.01)
