"""Same coverage as test_a7p.py + test_validate.py combined, but through
Profile.decode()/.encode() directly instead of a7p.load()/dump() -- this
needs no hashlib.md5, so it runs on firmware that lacks it (MICROPY_PY_SSL
off; see README.md's "Firmware dependency: hashlib.md5" section). Run from
the repo root, same convention as the other two:

    MICROPYPATH=micropython/natmod/build/x64 micropython micropython/tests/test_a7p_core.py

Not a replacement for test_a7p.py/test_validate.py -- those additionally
cover load()/dump() and the md5-prefixed file format, which this
deliberately skips.
"""
import a7p

with open("go/assets/example.a7p", "rb") as f:
    raw = f.read()

p = a7p.Profile()
assert p.decode(raw[32:])  # skip the 32-byte hex md5 prefix, no checksum check
assert p.has_profile
assert p.get_str("profile_name") == "338LM"
assert p.get_str("cartridge_name") == "UKROP 300GR HPBT"
assert p.get_str("bullet_name") == "UKROP 300GR HPBT"

prof = p.profile
assert (prof.zero_x, prof.zero_y, prof.sc_height) == (0, 0, 90)
assert prof.switches_count == 4
assert prof.distances_count == 197
assert (prof.distances[0], prof.distances[1], prof.distances[2]) == (0, 10000, 20000)
assert prof.coef_rows_count == 5
assert (prof.coef_rows[0].bc_cd, prof.coef_rows[0].mv) == (3820, 9110)
sw0 = prof.switches[0]
assert (sw0.c_idx, sw0.reticle_idx, sw0.zoom, sw0.distance, sw0.distance_from) == (255, 3, 0, 10000, 0)

# mutate through the zero-copy uctypes view, no re-decode
prof.zero_x = 12345
prof.distances[0] = 999
p.set_str("profile_name", "ROUNDTRIP")
assert p.profile.zero_x == 12345  # same buffer, read back immediately

encoded = p.encode()
p2 = a7p.Profile()
assert p2.decode(encoded)
assert p2.profile.zero_x == 12345
assert p2.profile.distances[0] == 999
assert p2.get_str("profile_name") == "ROUNDTRIP"
assert p2.profile.coef_rows[0].bc_cd == 3820

# known discrepancy: real sample data has distances[0] == 0 (just set to 999
# above), which the canonical schema (minimum 100) rejects
p2.profile.distances[0] = 0
try:
    p2.validate()
    raise AssertionError("expected A7PValidationError (distances[0]==0)")
except a7p.A7PValidationError:
    pass

# fix the one known-bad field, then it should validate clean
p2.profile.distances[0] = 100
p2.validate()

# sc_height out of [-5000, 5000]
p2.profile.sc_height = 999999
try:
    p2.validate()
    raise AssertionError("expected sc_height error")
except a7p.A7PValidationError:
    pass
p2.profile.sc_height = 90

# bc_type invalid enum
p2.profile.bc_type = 99
try:
    p2.validate()
    raise AssertionError("expected bc_type error")
except a7p.A7PValidationError:
    pass
p2.profile.bc_type = 0  # G1

# coef_rows mv duplicate (G1/G7 path, mv max 30000)
p2.profile.coef_rows[0].mv = 1000
p2.profile.coef_rows[1].mv = 1000
try:
    p2.validate()
    raise AssertionError("expected duplicate mv error")
except a7p.A7PValidationError:
    pass

print("OK")
