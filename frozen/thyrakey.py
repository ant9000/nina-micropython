import os, nrf_oberon
from time import time_ns

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

    @classmethod
    def sign(cls, our_key, our_pubkey, payload):
        assert len(our_key) == 32
        return cls(
            pubkey=our_pubkey,
            payload=payload,
            signature=nrf_oberon.ed25519_sign(our_key, our_pubkey, payload)
        )

class Challenge:
    def __init__(self, our_key, our_pubkey, their_pubkey):
        assert len(our_key) == 32
        assert len(our_pubkey) == 32
        assert len(their_pubkey) == 32
        self.our_key = our_key
        self.our_pubkey = our_pubkey
        self.their_pubkey = their_pubkey
        self.seed = os.urandom(16)
        self.challenge = SignedMessage.sign(self.our_key, self.our_pubkey, self.seed)

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
    CHALLENGE_TIMEOUT_NS = 1_000_000_000  # 1s

    def __init__(self, debug=False):
        super().__init__()
        self.owners = self._get_pubkey_list("owners.lst")
        self.blacklist = self._get_pubkey_list("blacklist.lst")
        self._state = {}
        self.debug = debug

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

    def print(self, msg):
        if self.debug:
            print(msg)

    def process_data(self, data):
        # ensure message is signed
        try:
            signed = SignedMessage.from_data(data)
        except:
            signed = None
        if not signed or not signed.is_valid():
            self.print("ERROR: Invalid payload")
            self._state = {}
            return None

        self.print(f"Payload: {signed.payload.hex()}")

        # expire pending challenge
        now = time_ns()
        challenge_ts = self._state.get("challenge_ts", None)
        if challenge_ts and now - challenge_ts > Door.CHALLENGE_TIMEOUT_NS:
            self.print("Pending challenge expired")
            self._state = {}

        if not "challenge" in self._state:
            challenge = Challenge(self.key, self.pubkey, self.pubkey)
            self.print(f"Challenge seed: {challenge.seed.hex()}")
            self._state = {
                'command': signed.data,
                'challenge': challenge,
                'challenge_ts': now
            }
            return challenge.data

        if self._state["challenge"].is_valid(signed.data):
            # user proved ownership of key corresponding to signed.pubkey
            elapsed = (now - self._state["challenge_ts"]) / 1_000_000
            self.print(f"Peer authenticated in {elapsed} ms")
            command = self._state["command"]
            payload = self.exec(signed.pubkey, command)
            if payload is not None:
                self.print(f"Command result: {payload.hex()}")
                answer = SignedMessage.sign(self.key, self.pubkey, payload)
        else:
            self.print("ERROR: peer authentication failed")
            answer = None
        self._state = {}
        return answer

    def exec(self, pubkey, command):
        answer = None
        if pubkey in self.pubkeys:
            # admin commands
            pass
        else:
            # user commands
            pass
        return answer
