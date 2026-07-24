# micropython/

A MicroPython native module exposing `.a7p` decode/encode, with
**zero-copy** field access via `uctypes` -- following the approach in
[ballistics-lab/micropython-bclibc](https://github.com/ballistics-lab/micropython-bclibc):
a native module fills a plain `bytearray`, and a `uctypes.struct` overlaid on
that same memory gives Python direct read/write access to fields, with no
intermediate object graph. Two ways to build/deploy it, sharing everything
except the C wiring:

* [`natmod/`](natmod/) -- a standalone `.mpy` you copy onto an
  already-flashed device, no firmware rebuild.
* [`usermod/`](usermod/) -- compiled directly into the firmware image via
  MicroPython's [User C
  Modules](https://docs.micropython.org/en/latest/develop/cmodules.html),
  works on any port regardless of natmod support, at the cost of a full
  firmware rebuild.

See "Building" below for natmod, and "usermod: compiling into the firmware
directly" for usermod.

Unlike that project, this one doesn't vendor a MicroPython checkout, Docker
cross-compilation containers, prebuilt binaries, or even nanopb itself --
you bring your own MicroPython source tree (`MPY_DIR`), `natmod/Makefile`
fetches the pinned nanopb commit on demand (`make fetch-nanopb`), and
everything else builds from source. There's also no math library dependency
to manage: `profedit.proto` has no `float`/`double` fields (everything is
`int32` or an enum), so this module needs nothing beyond
`memcpy`/`memset`/`memmove` (which `mpy_ld.py` resolves internally) and, on
targets without hardware integer divide, `libgcc.a`'s soft-divide helpers --
no `libm`, no picolibc/newlib math sources to patch.

## Layout

```
micropython/
  src/
    profedit.pb.h       nanopb-generated message structs (from proto/profedit.proto)
    profedit.pb.c       nanopb-generated field descriptors
    profedit.options    nanopb generator options (max_size/max_count -- see proto/)
    a7p_mp.c            the natmod itself: decode()/encode()/validate() (py/dynruntime.h)
    a7p_layout.h        generated offset/size constants + _Static_assert guards
    a7p_validate.h      generated numeric bounds (from schema/a7p.schema.json)
    a7p_validate_err.h  hand-written error-code enum + a7p_validate()'s prototype
    a7p_validate.c      hand-written bounds/enum/coef_rows checks, using the above
    a7p.py              pure-Python wrapper: Profile, load/loads/dump/dumps -- the
                        uctypes descriptor is generated in place between the
                        "# BEGIN/END GENERATED" markers, the rest is hand-written
  natmod/Makefile  `fetch-nanopb` clones nanopb into natmod/nanopb/ (gitignored,
                   not committed); builds natmod/build/$(ARCH)/{_a7p,a7p}.mpy
  usermod/
    micropython.cmake      top-level aggregator -- point USER_C_MODULES here for
                           CMake-based ports (rp2, esp32, ...)
    a7p/
      a7p_mod.c            same logic as src/a7p_mp.c, standard module-registration
                           API (py/runtime.h, MP_REGISTER_MODULE) instead of dynruntime.h
      micropython.mk        Make-based ports (unix, stm32, samd, nrf, ...) -- point
                           USER_C_MODULES at usermod/ (the parent), not this file
      micropython.cmake     included by the aggregator above
  NANOPB_COMMIT  the pinned nanopb commit -- single source of truth read by
                natmod/Makefile, usermod/a7p/micropython.mk, and
                usermod/a7p/micropython.cmake
  tools/gen_layout.py    regenerates src/a7p_layout.h + the generated block in a7p.py
  tools/gen_validate.py  regenerates src/a7p_validate.h from schema/a7p.schema.json
  tests/test_a7p.py       manual regression test, run under a real interpreter
  tests/test_validate.py  same, for Profile.validate()
```

## Why the layout is generated, not hand-written

`nanopb`, not us, decides `struct _profedit_Profile`'s field order, padding,
and the width of `pb_size_t` (the `*_count` fields) -- all of which
`tools/gen_layout.py` needs to get exactly right for a zero-copy `uctypes`
view to read/write the correct bytes. Rather than hand-deriving those offsets
(and re-deriving them by hand every time `proto/profedit.proto` changes), the
script compiles a tiny probe program against the real headers with
`offsetof()`/`sizeof()`, runs it, and emits both:

- `src/a7p_layout.h` -- `_Static_assert` guards, included by `a7p_mp.c`
- `src/a7p_layout.py` -- the `uctypes` descriptor, imported by `a7p.py`

Re-run it after regenerating `profedit.pb.h` (`scripts/generate_proto.sh`) or
touching the `PB_*`/`-fno-short-enums` flags below (needs nanopb fetched
first -- see Building):

```sh
cd micropython/natmod && make fetch-nanopb && cd ../..
python3 micropython/tools/gen_layout.py --cc gcc
```

**This actually matters, not just in theory:** cross-compiling this module
for `armv7m` (`arm-none-eabi-gcc`) during development hit a real portability
bug. That toolchain defaults to packing `profedit_DType`/`GType`/`TwistDir`
(each with 2-3 enumerators) into a single byte, while x86_64 gcc defaults to
4-byte enums -- silently shifting every `profedit_Profile` field from
`switches_count` onward relative to what `a7p_layout.py` (generated on the
host) expected. The `_Static_assert` guards caught it immediately as a build
failure instead of a silent wrong-memory read. The fix, already applied in
both `natmod/Makefile` and `gen_layout.py`, is pinning `-fno-short-enums`
unconditionally -- verified byte-identical across x86_64, `arm-none-eabi-gcc`
(`armv7m`), and `riscv64-unknown-elf-gcc` (`rv32imc`) after the fix.

## Building

Requires a local MicroPython checkout (for `mpy-cross`, `mpy_ld.py` and
`py/dynruntime.mk`), the matching cross-compiler for your target, and the
`pyelftools` and `ar` Python packages that `mpy_ld.py` needs to link
prebuilt `.a` archives:

```sh
git clone https://github.com/micropython/micropython
(cd micropython/mpy-cross && make)
pip install pyelftools ar

cd micropython/natmod   # this directory, inside the a7p repo
make fetch-nanopb                              # once; clones the pinned commit into ./nanopb
make MPY_DIR=/path/to/micropython ARCH=x64 dist
```

`fetch-nanopb` re-clones into `./nanopb` (gitignored) every time it's run --
harmless to re-run, but don't hand-edit anything under there.

`ARCH` is one of `x86, x64, armv6m, armv7m, armv7emsp, armv7emdp, xtensa,
xtensawin, rv32imc, rv64imc`. This produces:

```
natmod/build/<ARCH>/_a7p.mpy   the native module
natmod/build/<ARCH>/a7p.mpy    the Python wrapper (mpy-cross compiled)
```

Copy both to the device (e.g. `mpremote cp build/armv6m/*.mpy :`) --
`import a7p` pulls in `_a7p` itself.

### Which `ARCH` for which port

`ARCH` picks a CPU architecture, not a port -- whether a given port's stock
firmware can actually `import` a natmod .mpy for that architecture depends on
whether that port enables native code emission (`MICROPY_EMIT_*`) by default,
which is a separate, per-port thing from this Makefile. Checked directly
against the default `mpconfigport.h`/`mpconfigboard.h`/`mpconfigmcu.h` in a
MicroPython checkout (not assumed):

| `ARCH` | Ports enabling it by default | Notes |
| --- | --- | --- |
| `x64` / `x86` | `unix` | `windows` explicitly sets `MICROPY_EMIT_X64 (0)` and `MICROPY_EMIT_THUMB (0)` -- natmod does **not** import there even though it's an x86 target. |
| `armv6m` | `rp2` (original RP2040, Cortex-M0+) | |
| `armv7m` / `armv7emsp` / `armv7emdp` | `stm32`, `mimxrt`, `alif`, `renesas-ra`, `psoc-edge` | Exact Cortex-M variant (M3/M4F/M7) depends on the board's MCU. |
| (same, ARM) | `nrf`, `samd` | Conditional on a board/MCU feature flag (`EXTRA_FEAT` on nrf, `SAMD21_EXTRA_FEATURES` on samd21; samd51 always on) -- may be off in a given board's stock firmware even though the port supports it. |
| `xtensa` | `esp8266` | Set at board level (`mpconfigboard.h`), not port level. |
| `xtensawin` | `esp32` (ESP32, ESP32-S3) | |
| `rv32imc` | `esp32` (ESP32-C3/C6/H2), `rp2` (RP2350 in RISC-V mode), `zephyr` | |
| `rv64imc` | none by default | No stock port enables a 64-bit RISC-V native emitter currently. |

The most reliably "just works" targets: **`unix`** (`x64`, what's actually
been tested here) and **`rp2`**/**`esp32`** official firmware (`armv6m`,
`xtensawin`, `rv32imc`). Anywhere else, check that specific board's config
before assuming natmod will import.

**Not supported**: WebAssembly. This isn't a bug to fix, it's a mismatch of
mechanism -- `natmod`/`mpy_ld.py` links native machine code for a fixed set
of real ISAs (the `ARCH` list above), and WebAssembly isn't one of them.
Running this in MicroPython-in-the-browser would mean compiling everything
(interpreter + this module) from source into one Emscripten build instead
(the "user C module" path, not natmod) -- out of scope here.

**Why a Makefile and not a `CMakeLists.txt`**: upstream MicroPython's natmod
tooling (`py/dynruntime.mk`, `tools/mpy_ld.py`) is Make-only -- every example
under `examples/natmod/` in the MicroPython source is a Makefile that
`include`s `dynruntime.mk`, and there's no CMake equivalent shipped for it.
(CMake shows up in the MicroPython ecosystem for *usermod* -- firmware
embedded at build time -- on the `rp2`/`esp32` ports specifically, because
their underlying SDKs (pico-sdk, esp-idf) are CMake-based; that's a
different mechanism from natmod, see above.) Hand-rolling a `CMakeLists.txt`
here would mean reimplementing `dynruntime.mk`'s logic (arch flags, QSTR
preprocessing, invoking `mpy_ld.py`) ourselves, for no benefit and a real
risk of drifting out of sync whenever upstream changes it.

**Verification per target**, so it's clear what's actually been checked
rather than assumed:

| ARCH | Checked |
| --- | --- |
| `x64` | Full functional test under MicroPython's real unix port (`tests/test_a7p.py`): decodes `go/assets/example.a7p`, every field cross-checked against `py/src/a7p`'s `google.protobuf`-based decode of the same file, mutated through the `uctypes` view with no re-decode, re-encoded, reloaded byte-for-byte. |
| `armv7m` (`arm-none-eabi-gcc`) | Struct layout verified byte-identical to x64 (`offsetof`/`sizeof` probe); natmod links cleanly. Not run under an emulator. |
| `rv32imc`, `rv64imc` (`riscv64-unknown-elf-gcc` + picolibc) | Same: layout verified identical, natmod links cleanly against picolibc with no relocation errors -- notably, [micropython-bclibc](https://github.com/ballistics-lab/micropython-bclibc)'s RISC-V notes describe a real `mpy_ld.py`/picolibc linking bug, but that's specifically about linking picolibc's math functions (`sin`/`cos`/`sqrt`/...); this module never links anything beyond `libgcc.a` (no floats anywhere in `profedit.proto`), so it doesn't hit that code path. |
| `armv6m`, `armv7emsp`, `armv7emdp`, `xtensa`, `xtensawin`, `x86` | Not attempted (no toolchain available in the environment this was built in). Expected to work the same way as the other embedded targets above, since the module has no arch-specific code, but this is unverified -- treat it as such until someone builds and runs it on real hardware. |

## usermod: compiling into the firmware directly

`natmod` above produces a standalone `.mpy` you copy onto an *already-flashed*
device -- no firmware rebuild needed, but it only imports on a build that has
native-code loading enabled for its architecture (see the table above). The
alternative is [User C
Modules](https://docs.micropython.org/en/latest/develop/cmodules.html)
(`usermod`): compile the same module straight into the firmware image, which
works on any port regardless of natmod support, at the cost of a full
firmware rebuild whenever the module changes.

`micropython/usermod/` provides both a `micropython.mk` (Make-based ports)
and `micropython.cmake` (CMake-based ports) -- MicroPython's own docs
recommend shipping both so a module works on every port, since a given port
only reads whichever one matches its own build system. Point
`USER_C_MODULES` at it as one extra flag on the build command you'd already
run for that port:

```sh
git clone https://github.com/micropython/micropython
cd micropython && git submodule update --init --recursive

# Make-based ports (unix, stm32, samd, nrf, mimxrt, esp8266, ...): point
# USER_C_MODULES at the *directory* -- it globs */micropython.mk one level
# down, so this must be the parent of usermod/a7p/, not that directory itself.
cd ports/unix
make USER_C_MODULES=/path/to/a7p/micropython/usermod

# CMake-based ports (rp2, esp32): point USER_C_MODULES at the aggregator
# .cmake file directly instead.
cd ports/rp2
cmake -B build -DUSER_C_MODULES=/path/to/a7p/micropython/usermod/micropython.cmake
cmake --build build
```

Then copy `micropython/src/a7p.py` onto the device's filesystem after
flashing (`mpremote cp micropython/src/a7p.py :`) -- it isn't frozen into
the firmware image, to avoid a second required flag (`FROZEN_MANIFEST`) and
per-port testing of freezing behavior; `import a7p` works the same either
way once it's present.

Checked empirically against ports supporting `USER_C_MODULES` (every
Make-based port includes `py/py.mk`, which is where that support actually
lives, regardless of whether the port's own `Makefile` mentions
`USER_C_MODULES` by name -- checked directly, not assumed):

* **Supported**: `unix`, `stm32`, `samd`, `nrf`, `mimxrt`, `esp8266`, `alif`,
  `renesas-ra`, `psoc-edge`, `windows`, `webassembly`, `qemu`, `cc3200`,
  `bare-arm`, `minimal`, `pic16bit` (Make-based, via `py/py.mk`), plus `rp2`
  and `esp32` (CMake-based, `USER_C_MODULES` in their own `CMakeLists.txt`).
* **Not supported**: `zephyr` (its own Kconfig/west module system, no
  `Makefile` at all, and its `CMakeLists.txt` doesn't reference
  `USER_C_MODULES`); `embed` (not a standalone port -- a library meant to be
  embedded into someone else's build, no `Makefile`/`CMakeLists.txt` of its
  own).

### nanopb: fetched automatically, no extra step

Neither `micropython.mk` nor `micropython.cmake` require a separate
`fetch-nanopb` step (unlike `natmod/Makefile`) -- both fetch the same pinned
commit (`micropython/NANOPB_COMMIT`, the single source of truth all three
build paths read from) themselves, automatically, the first time they're
processed:

* `micropython.mk` does it with a `$(shell git clone ...)` guarded by a
  does-it-exist check, evaluated at Makefile-parse time (before any compile
  rule runs) -- this works identically regardless of which port's `Makefile`
  includes it, since it's plain shell.
* `micropython.cmake` uses `FetchContent_Declare` + `FetchContent_Populate`
  (deliberately *not* `FetchContent_MakeAvailable`, which would also
  `add_subdirectory()` nanopb's own `CMakeLists.txt` -- pulling in its code
  generator, which needs a local `protoc`, and its own compiled library
  target, neither of which this module needs since it compiles
  `pb_common.c`/`pb_decode.c`/`pb_encode.c` itself as plain sources).

Both write into the same shared `micropython/natmod/nanopb/` directory
`natmod/Makefile`'s own `fetch-nanopb` uses, so building natmod once and
usermod once doesn't fetch nanopb twice.

Verified end-to-end: rebuilt the unix port with
`USER_C_MODULES=micropython/usermod` (confirms the Make path, the `*/micropython.mk`
directory convention, and the auto-fetch all work together; `import _a7p`
succeeds and the same `tests/test_a7p.py`/`tests/test_validate.py` pass
against it). The CMake path (`micropython.cmake`) was verified by pointing a
minimal standalone CMake project at it: `FetchContent_Populate` correctly
fetches nanopb with no `protoc` dependency, and every source file except the
module's own C wrapper (which needs the real `py/obj.h` etc. that only an
actual port's build tree provides) compiles cleanly through the generated
`target_sources`/`target_include_directories`/`target_compile_definitions`
wiring. Not built against real `rp2`/`esp32` SDKs (pico-sdk/esp-idf,
substantial toolchains not available in the environment this was built in).

## Usage

```python
import a7p

with open("MyProfile.a7p", "rb") as fp:
    profile = a7p.load(fp)        # or a7p.loads(data) from raw bytes

print(profile.get_str("profile_name"))
print(profile.profile.zero_x, profile.profile.sc_height)

# direct, zero-copy field access -- no re-decode needed to see writes
profile.profile.zero_x = 100
profile.profile.distances[0] = 5000
profile.profile.switches[0].zoom = 2
profile.set_str("profile_name", "My Profile")

with open("MyProfile_edited.a7p", "wb") as fp:
    a7p.dump(profile, fp)         # or data = a7p.dumps(profile)
```

`load`/`dump` take an already-open binary file object, not a path -- same
convention as `json.load`/`json.dump` (and `py/src/a7p/a7p.py`'s own
`load`/`dump`).

`profile.profile` is the `uctypes` struct over `profedit_Profile` --
`switches`/`distances`/`coef_rows` are `uctypes` arrays (of `SwPos`/`int32`/
`CoefRow` respectively), and `switches_count`/`distances_count`/
`coef_rows_count` are the corresponding element counts nanopb wrote on
decode. Fixed `char[]` string fields (`profile_name`, `cartridge_name`,
`bullet_name`, `short_name_top`, `short_name_bot`, `user_note`, `caliber`,
`device_uuid`) aren't part of the `uctypes` descriptor -- `uctypes` has no
"fixed char array as str" type -- so they go through `get_str`/`set_str`
instead, which slice the same backing buffer directly.

`Profile.decode()`/`.encode()` work with the raw protobuf body (no md5
prefix); `load`/`loads`/`dump`/`dumps` handle the full `.a7p` file format
(32-byte hex md5 prefix + protobuf body), mirroring `py/src/a7p/a7p.py`'s
API. `A7PChecksumError` and `A7PDecodeError` (both `A7PError`) cover a bad
md5 prefix and a malformed protobuf body, respectively. Neither `load` nor
`loads` validates value bounds -- call `profile.validate()` explicitly (see
below) if you need that; it's opt-in since some real `.a7p` files fail one
canonical rule (see below) and this shouldn't silently break loading them.

Requires `hashlib.md5` (`MICROPY_PY_HASHLIB_MD5`, which defaults to whatever
`MICROPY_PY_SSL` is set to -- on by default on the unix port) for
`load`/`loads`/`dump`/`dumps`; `Profile.decode`/`.encode`/`.validate` alone
don't need it.

## Validating field bounds

`decode()` (via nanopb) and the fixed-size `uctypes`/buffer layout already
enforce, for free, everything that's structural: string lengths (buffer
size), repeated-field counts (nanopb rejects wire data with more elements
than `max_count`; `uctypes` array access raises `IndexError` past the
declared count -- verified, not assumed). What's *not* checked anywhere
above is whether a *value* is semantically valid -- e.g. `sc_height` within
[-5000, 5000], `bc_type` being one of the three valid enum values, or the
`coef_rows` count/mv-range rule that depends on `bc_type` -- since none of
that constrains the wire format or the C struct, only the schema.

```python
profile.profile.sc_height = 999999   # decodes/encodes fine, structurally valid
profile.validate()                   # raises A7PValidationError: "sc_height: out of range"
```

`Profile.validate()` calls into `a7p_validate()` (`src/a7p_validate.c`),
which returns the first failing rule as a small int the Python side maps to
a message (`_VALIDATE_MESSAGES` in `a7p.py`). The ~30 numeric thresholds it
checks against are generated by `tools/gen_validate.py` straight from
`schema/a7p.schema.json` into `src/a7p_validate.h` -- re-run it (no nanopb
checkout needed, just `python3 micropython/tools/gen_validate.py`) whenever
the schema changes. The *shape* of the checks (which fields get a plain
min/max, the `bc_type`-conditional `coef_rows` bounds, the mv-unique-except-0
rule) is hand-written once in `a7p_validate.c`, same as every other a7p
language binding's validator has to -- none of that is generically derivable
from JSON Schema either (the schema's own note on `coef_rows` says as much:
"Enforce with one small hand-written check per language"). Total added
`.mpy` size for all of this: about 900 bytes of machine code.

This deliberately isn't a generic JSON-Schema-to-C compiler -- no a7p
language binding has one of those (even `go`'s validator is a runtime
JSON-Schema engine, not codegen); `gen_validate.py` only keeps `a7p_validate.c`'s
numeric constants in sync with the schema, not its logic.

One canonical rule is known to reject real, existing data: `distances[]`
items must be in `[100, 300000]`, but `go/assets/example.a7p` (and
`dump.a7p`/`switches.a7p`, same underlying data) has `distances[0] == 0`.
This is a pre-existing schema/data discrepancy documented in
`docs/DESIGN-schema-unification.md`, not a bug in `a7p_validate.c` --
`tests/test_validate.py` asserts this exact failure rather than working
around it.

## Running the tests

```sh
cd micropython/natmod && make MPY_DIR=/path/to/micropython ARCH=x64 dist
cd ../..
MICROPYPATH=micropython/natmod/build/x64 /path/to/micropython/ports/unix/build-standard/micropython micropython/tests/test_a7p.py

cd go/assets
MICROPYPATH=../../micropython/natmod/build/x64 /path/to/micropython/ports/unix/build-standard/micropython ../../micropython/tests/test_validate.py
```
