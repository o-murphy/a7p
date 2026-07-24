"""Manual regression test for the a7p natmod, run under a real MicroPython
interpreter (e.g. the unix port) with the built natmod on MICROPYPATH.

    cd micropython/natmod && make MPY_DIR=/path/to/micropython ARCH=x64 dist
    MICROPYPATH=natmod/build/x64 micropython micropython/tests/test_a7p.py

Cross-checked against py/src/a7p (the canonical google.protobuf-based
implementation) decoding the same file -- see the commit that introduced
this file for the exact comparison run.
"""
import sys

sys.path.append("go/assets")  # when run from the repo root

import a7p

ASSET = "go/assets/example.a7p"

with open(ASSET, "rb") as f:
    p = a7p.load(f)
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

with open("/tmp/a7p_roundtrip_test.a7p", "wb") as f:
    a7p.dump(p, f)

with open("/tmp/a7p_roundtrip_test.a7p", "rb") as f:
    p2 = a7p.load(f)
assert p2.profile.zero_x == 12345
assert p2.profile.distances[0] == 999
assert p2.get_str("profile_name") == "ROUNDTRIP"
assert p2.profile.coef_rows[0].bc_cd == 3820

print("OK")
