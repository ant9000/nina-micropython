import os, time, nrf_oberon

s = time.time_ns()
seed = os.urandom(32)
e = (time.time_ns() - s) // 1000000
print(f"Seed: {seed.hex()} [{e} ms]")

s = time.time_ns()
pub = nrf_oberon.ed25519_public_key(seed)
e = (time.time_ns() - s) // 1000000
print(f"Pubkey: {pub.hex()} [{e} ms]")

msg = "Hello, World!"
print(f"Message: '{msg}'")

s = time.time_ns()
sig = nrf_oberon.ed25519_sign(seed, pub, msg)
e = (time.time_ns() - s) // 1000000
print(f"Signature: {sig.hex()} [{e} ms]")

s = time.time_ns()
vfy = nrf_oberon.ed25519_verify(pub, sig, msg)
e = (time.time_ns() - s) // 1000000
print(f"Verified? {vfy} [{e} ms]")
