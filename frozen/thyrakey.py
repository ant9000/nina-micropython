import os, nrf_oberon

class SignedMessage:
    def __init__(self, pubkey, payload, signature):
        assert len(pubkey) == 32
        assert len(payload) > 0
        assert len(signature) == 64
        self.pubkey = pubkey
        self.payload = payload
        self.signature = signature

    @classmethod
    def from_data(cls, data):
        assert len(data) > 32 + 64 # at least 1 byte of payload is required
        return cls(pubkey=data[:32], payload=data[32:-64], signature=data[-64:])

    @property
    def data(self):
        return self.pubkey + self.payload + self.signature

    def is_valid(self):
        return nrf_oberon.ed25519_verify(self.pubkey, self.signature, self.payload)

class Challenge:
    def __init__(self, our_key, our_pubkey, their_pubkey):
        assert len(our_key) == 32
        assert len(our_pubkey) == 32
        assert len(their_pubkey) == 32
        self.our_key = our_key
        self.our_pubkey = our_pubkey
        self.their_pubkey = their_pubkey
        self.seed = os.urandom(16)
        self.challenge = SignedMessage(
            pubkey=self.our_pubkey,
            payload=self.seed,
            signature=nrf_oberon.ed25519_sign(self.our_key, self.our_pubkey, self.seed)
        )

    @property
    def data(self):
        return self.challenge.data

    def is_valid(self, answer):
        msg = SignedMessage.from_data(answer)
        return msg.is_valid() and msg.pubkey == self.their_pubkey and msg.payload == self.seed

class Identity:
    def __init__(self):
        self.key, self.pubkey = self._get_keypair()

    def _get_keypair(self):
        try:
            data = open("key.bin", "rb").read()
            assert len(data) == 64
            key = data[:32]
            pubkey = data[32:]
        except:
            key = os.urandom(32)
            pubkey = nrf_oberon.ed25519_public_key(key)
            open("key.bin", "wb").write(key + pubkey)
        return (key, pubkey)

class Door(Identity):
    def __init__(self):
        super().__init__()
        self.owners = self._get_pubkey_list("owners.lst")
        self.blacklist = self._get_pubkey_list("blacklist.lst")

    def _get_pubkey_list(self, fname):
        pubkeys = []
        try:
            with open(fname, "rb") as f:
                while True:
                    pubkey = f.read(32)
                    if pubkey:
                        assert len(pubkey) == 32
                        pubkeys.append(pubkey)
                    else:
                        break
        except OSError:
            pass
        return pubkeys
