# micropython/

A MicroPython [dynamic native module](https://docs.micropython.org/en/latest/develop/natmod.html)
(natmod) exposing `.a7p` decode/encode, with **zero-copy** field access via
`uctypes` -- following the approach in
[ballistics-lab/micropython-bclibc](https://github.com/ballistics-lab/micropython-bclibc):
a native module fills a plain `bytearray`, and a `uctypes.struct` overlaid on
that same memory gives Python direct read/write access to fields, with no
intermediate object graph.

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
    profedit.pb.h    nanopb-generated message structs (from proto/profedit.proto)
    profedit.pb.c    nanopb-generated field descriptors
    profedit.options nanopb generator options (max_size/max_count -- see proto/)
    a7p_mp.c         the natmod itself: decode()/encode() (py/dynruntime.h)
    a7p_layout.h     generated offset/size constants + _Static_assert guards
    a7p_layout.py    generated uctypes descriptor (must match a7p_layout.h)
    a7p.py           pure-Python wrapper: Profile, load/loads/dump/dumps
  natmod/Makefile  `fetch-nanopb` clones nanopb into natmod/nanopb/ (gitignored,
                   not committed); builds natmod/build/$(ARCH)/{_a7p,a7p_layout,a7p}.mpy
  tools/gen_layout.py  regenerates src/a7p_layout.{h,py} from the real compiled struct
  tests/test_a7p.py    manual regression test, run under a real interpreter
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
xtensawin, rv32imc, rv64imc` (see `$(MPY_DIR)/py/dynruntime.mk` for what each
maps to -- e.g. `armv6m` for RP2040, `rv32imc` for ESP32-C3). This produces:

```
natmod/build/<ARCH>/_a7p.mpy         the native module
natmod/build/<ARCH>/a7p_layout.mpy   generated uctypes descriptor (mpy-cross compiled)
natmod/build/<ARCH>/a7p.mpy          the Python wrapper (mpy-cross compiled)
```

Copy all three to the device (e.g. `mpremote cp build/armv6m/*.mpy :`) --
`import a7p` pulls in the other two.

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

## Usage

```python
import a7p

profile = a7p.load("MyProfile.a7p")       # or a7p.loads(data)
print(profile.get_str("profile_name"))
print(profile.profile.zero_x, profile.profile.sc_height)

# direct, zero-copy field access -- no re-decode needed to see writes
profile.profile.zero_x = 100
profile.profile.distances[0] = 5000
profile.profile.switches[0].zoom = 2
profile.set_str("profile_name", "My Profile")

a7p.dump(profile, "MyProfile_edited.a7p")  # or data = a7p.dumps(profile)
```

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
md5 prefix and a malformed protobuf body, respectively.

Requires `hashlib.md5` (`MICROPY_PY_HASHLIB_MD5`, which defaults to whatever
`MICROPY_PY_SSL` is set to -- on by default on the unix port) for
`load`/`loads`/`dump`/`dumps`; `Profile.decode`/`.encode` alone don't need it.

## Running the test

```sh
cd micropython/natmod && make MPY_DIR=/path/to/micropython ARCH=x64 dist
cd ../..
MICROPYPATH=micropython/natmod/build/x64 /path/to/micropython/ports/unix/build-standard/micropython micropython/tests/test_a7p.py
```
