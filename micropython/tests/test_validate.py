"""Manual regression test for Profile.validate() (a7p_validate.c), run under
a real MicroPython interpreter with the built natmod on MICROPYPATH, from
inside go/assets/ (or with that directory copied alongside this script):

    cd micropython/natmod && make MPY_DIR=/path/to/micropython ARCH=x64 dist
    cd ../../go/assets
    MICROPYPATH=../../micropython/natmod/build/x64 micropython ../../micropython/tests/test_validate.py
"""
import a7p

with open("example.a7p", "rb") as f:
    p = a7p.load(f)

# known discrepancy: real sample data has distances[0] == 0, which the
# canonical schema (minimum 100) rejects
try:
    p.validate()
    print("FAIL: expected A7PValidationError (distances[0]==0)")
except a7p.A7PValidationError as e:
    print("OK expected failure:", e)

# fix the one known-bad field, then it should validate clean
p.profile.distances[0] = 100
p.validate()
print("OK validates clean after fixing distances[0]")

# now break something on purpose: sc_height out of [-5000, 5000]
p.profile.sc_height = 999999
try:
    p.validate()
    print("FAIL: expected sc_height error")
except a7p.A7PValidationError as e:
    print("OK sc_height error:", e)
p.profile.sc_height = 90

# bc_type invalid enum
p.profile.bc_type = 99
try:
    p.validate()
    print("FAIL: expected bc_type error")
except a7p.A7PValidationError as e:
    print("OK bc_type error:", e)
p.profile.bc_type = 0  # G1

# coef_rows mv duplicate (G1/G7 path, mv max 30000)
p.profile.coef_rows[0].mv = 1000
p.profile.coef_rows[1].mv = 1000
try:
    p.validate()
    print("FAIL: expected duplicate mv error")
except a7p.A7PValidationError as e:
    print("OK duplicate mv error:", e)

print("ALL VALIDATE TESTS OK")
