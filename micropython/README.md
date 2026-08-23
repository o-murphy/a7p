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
directly" for usermod. **Use natmod wherever it works** (see the ARCH table
below) -- usermod is the fallback for the few places natmod categorically
can't reach (no matching architecture in `dynruntime.mk`, or the port
disables native code loading outright), like `webassembly`, `unix` on
aarch64, or `windows` (any architecture). CI follows this policy directly:
it builds every natmod ARCH, and the `usermod` jobs only cover
`webassembly`, `unix` on `aarch64`/`armhf`/`mipsel`, and `windows` -- natmod
already covers everywhere else.

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
    a7p_mp.c            the natmod itself: decode()/encode()/validate()/clamp()/md5()
                        (py/dynruntime.h)
    a7p_layout.h        generated offset/size constants + _Static_assert guards
    a7p_validate.h      generated numeric bounds (from schema/a7p.schema.json)
    a7p_validate_err.h  hand-written error-code enum + a7p_validate()/a7p_clamp()
                        prototypes
    a7p_validate.c      hand-written bounds/enum/coef_rows checks (a7p_validate) and
                        their in-place fix-up counterpart (a7p_clamp), using the above
    md5.c, md5.h        vendored public-domain MD5 (Solar Designer) -- load()/dump()'s
                        checksum, independent of the target firmware's hashlib
    a7p.py              pure-Python wrapper: Profile, load/loads/dump/dumps -- the
                        uctypes descriptor is generated in place between the
                        "# BEGIN/END GENERATED" markers, the rest is hand-written
  natmod/Makefile  `fetch-nanopb` clones nanopb into natmod/nanopb/ (gitignored,
                   not committed); builds natmod/build/$(ARCH)/a7p.mpy (single
                   file -- C and Python sources merged, see SRC in that Makefile)
  usermod/
    micropython.cmake      top-level aggregator -- point USER_C_MODULES here for
                           CMake-based ports (rp2, esp32, ...)
    manifest.py             freezes src/a7p.py into the firmware -- include()
                           it from a custom FROZEN_MANIFEST (see usermod
                           section below), not used by USER_C_MODULES itself
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
  tests/test_a7p_core.py  same coverage as both above combined, via decode()/encode()
                         directly instead of load()/dump() -- skips the md5 prefix
                         entirely, so it's the one test file with zero filesystem/
                         checksum surface, useful as a minimal smoke test
  tests/run_wasm_tests.mjs  Node harness running all three test files above against
                           a built ports/webassembly micropython.mjs (see usermod section)
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
natmod/build/<ARCH>/a7p.mpy   native (C) and Python parts merged into one file
```

### Running an ARM natmod on an ARM Linux host

CI executes `x64` on the runner and builds the other nine. Two of the ARM
ARCHes can also be *executed*, on real ARM silicon and without a board: the
`natmod (armv7emsp | armv7emdp / 32-bit ARM Linux)` jobs build a statically
linked 32-bit armhf `ports/unix` interpreter on `ubuntu-24.04-arm` -- which
runs AArch32 on its own CPU -- and load the `.mpy` into it.

It is allowed because `py/persistentcode.h` gives a Thumb-2 host with a
double-precision FPU `MPY_FEATURE_ARCH = MP_NATIVE_ARCH_ARMV7EMDP`, and the
compatibility test is a *range* (`ARMV6M <= x <= that`), not an equality.

Only those two, because that check says nothing about the **float ABI**.
`py/dynruntime.mk` gives `armv6m` and `armv7m` no `-mfloat-abi=hard`, so their
floats reach the runtime in core registers while an armhf host reads them from
VFP registers. The `.mpy` loads and then returns wrong values instead of
failing, so do not try it.

The host must be linked `-static`: an arm64 runner executes AArch32 but ships
no armhf glibc, so a dynamically linked binary cannot find
`/lib/ld-linux-armhf.so.3` and dies with exit 127 before MicroPython starts.

This proves the native module and its relocations are right on real ARM
silicon. It is not a board, and it is not the bare-metal firmware environment
that `mp-usermod.yml`'s `qemu-armv7m` job covers.

What that job actually guards is worth stating: `ports/qemu/Makefile:74` links
`-nostdlib` with `libgcc` alone, so a usermod there has **no libc and no libm at
all**. That holds for this module -- no `malloc`, no `math`, no `printf`
anywhere in `micropython/src` or `micropython/usermod` -- and the job exists to
keep it true rather than to assume it: a dependency on either would stop
linking, which is exactly the signal wanted.
`ballistics-lab/micropython-bclibc` runs the same job for the same reason.
`o-murphy/micropython-wasm3` cannot: wasm3 allocates through the port's
`calloc()`, and supplying its own shims would link and then corrupt, because
they allocate on the GC heap while a usermod's globals sit in firmware `.bss`
that `gc_collect()` does not scan.

Copy it to the device (e.g. `mpremote cp build/armv6m/a7p.mpy :`) -- `import a7p`
is all that's needed, there's no separate module to also copy.

### Which `ARCH` for which port

`ARCH` picks a CPU architecture, not a port -- whether a given port's stock
firmware can actually `import` a natmod .mpy for that architecture depends on
whether that port enables native code emission (`MICROPY_EMIT_*`) by default,
which is a separate, per-port thing from this Makefile.

**Not supported**: WebAssembly. This isn't a bug to fix, it's a mismatch of
mechanism -- `natmod`/`mpy_ld.py` links native machine code for a fixed set
of real ISAs, and WebAssembly isn't one of them. Running this in
MicroPython-in-the-browser would mean compiling everything (interpreter +
this module) from source into one Emscripten build instead (the "user C
module" path, not natmod) -- out of scope here.

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

**Per-port natmod/usermod support and what's actually verified in CI right
now** (this table is the maintained source of truth for this -- kept in
`mp.md` rather than duplicated by hand here, so update that file, not this
list, when CI coverage changes):

<!-- BEGIN mp.md (kept in sync by hand -- see that file) -->

- 🔷 covered by `natmod`, 🔶 covered by `usermod`, ➖ not in CI

| port                       | arch                                          | natmod support | usermod support | current CI build | implementation (as wired in `.github/workflows/mp-natmod.yml` / `.github/workflows/mp-usermod.yml`)                                                                                                                                                                                                                                                 |
| -------------------------- | --------------------------------------------- | :------------: | :-------------: | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| unix                       | `x64`, `x86`                                  |       ✔️        |        ✔️        | 🔷 🔶             | the `natmod (x64)` / `natmod (x86)` jobs build and run the natmod path; `usermod` rows of the same names build and run the usermod path on the same runner (`x86` via `MICROPY_FORCE_32BIT=1`). Both are kept because the two modes fail differently — a usermod links against the port's own libc, a natmod against dynruntime |
| unix                       | `aarch64`                                     |       ❌        |        ✔️        | 🔶                | `usermod` job, `port: unix`, `arch_label: aarch64`, `runs_on: ubuntu-24.04-arm` — native build, no cross-compiler                                                                                                                                                                                                |
| unix                       | `armhf`                                       |       ❌        |        ✔️        | 🔶                | dedicated `usermod-cross` job (`arch_label: armhf`), `runs_on: ubuntu-24.04-arm` — cross-built with `CROSS_COMPILE=arm-linux-gnueabihf-`, `VARIANT=coverage`, `MICROPY_STANDALONE=1`, `make deplibs` as its own step, `LDFLAGS_EXTRA=-static`, then **run on the arm64 runner's own CPU — no qemu, no binfmt handler**. Build recipe still follows upstream's `tools/ci.sh` `ci_unix_qemu_arm_*`; execution and the `hf` ABI deliberately do not (see that job's comment) |
| unix                       | `mipsel`                                       |       ❌        |        ✔️        | 🔶                | same dedicated `usermod-cross` job (`arch_label: mipsel`) — little-endian, deliberately not upstream's big-endian `mips-linux-gnu`: this module hardcodes `uctypes.LITTLE_ENDIAN` (a7p.py) over memory nanopb populates in the host's native byte order, so big-endian genuinely mismatches (confirmed by a real CI run: build+QEMU run succeeded, `test_a7p.py`'s zero_x/zero_y/sc_height assertion failed). Proven working on mipsel by ballistics-lab/micropython-bclibc's own CI |
| windows                    | `x86`                                         |       ❌        |        ✔️        | 🔶                | `usermod` job, `arch_label: x86`, `runs_on: windows-latest`, MSYS2 MINGW32 (`mingw-w64-i686-gcc`, no CROSS_COMPILE) — native build+run (WOW64), same recipe as upstream's `build-mingw` job                                                                                                                      |
| windows                    | `x64`                                         |       ❌        |        ✔️        | 🔶                | `usermod` job, `arch_label: x64`, `runs_on: windows-latest`, MSYS2 MINGW64 (`mingw-w64-x86_64-gcc`, no CROSS_COMPILE) — native build+run, same upstream recipe                                                                                                                                                   |
| windows                    | `arm64`                                       |       ❌        |        ✔️        | 🔶                | `usermod` job, `arch_label: arm64`, `runs_on: windows-11-arm`, MSYS2 CLANGARM64 (`mingw-w64-clang-aarch64-gcc-compat` + `-clang`) — native build+run. Needs four MicroPython-build-system overrides plus `CFLAGS_EXTRA=-Wno-error`; see that row's own comment for each |
| webassembly                | `wasm`                                        |       ❌        |        ✔️        | 🔶                | `usermod` job, `port: webassembly`, `variant: pyscript`, `runs_on: ubuntu-latest`, tests via `run_wasm_tests.mjs` — full suite (module now uses its own vendored `_a7p._md5()`, not `hashlib.md5`)                                                                                                                |
| rp2                        | `armv6m`, `armv7emsp`, `armv7emdp`, `rv32imc` |       ✔️        |        ✔️        | 🔷 🔶             | `natmod` job builds all 4 ARCHes; plus a `usermod-rp2040` job that builds `BOARD=RPI_PICO` firmware and **runs** `test_a7p_core.py` on it under the rp2040py emulator. That execution is the point: natmod builds `armv6m` and never runs it, so this is the only RP2040 execution this project has |
| esp32                      | `xtensawin` (+ `rv32imc` for C3/C6)           |       ✔️        |        ✔️        | 🔷 🔶             | `natmod` job, `arch: xtensawin`; plus a `usermod-esp32` **build-only** job (`BOARD=ESP32_GENERIC`, ESP-IDF v5.5.1) — there is no esp32 emulator to run a firmware image on, so that job proves the module links into a real esp32 firmware and nothing more |
| esp8266                    | `xtensa`                                      |       ✔️        |        ✔️        | 🔷                | `natmod` job, `arch: xtensa`; usermod explicitly excluded — stock firmware overflows `iram1_0_seg`                                                                                                                                                                                                               |
| stm32                      | `armv6m`, `armv7m`, `armv7emsp`, `armv7emdp`  |       ✔️        |        ✔️        | 🔷                | `natmod` job covers all 4 ARCHes (except tiny-flash boards); usermod deliberately not added                                                                                                                                                                                                                      |
| samd                       | `armv7emsp`                                   |       ✔️        |        ✔️        | 🔷                | `natmod` job, `arch: armv7emsp` (M4/SAMD51 only, M0 conditional); usermod deliberately not added                                                                                                                                                                                                                 |
| nrf                        | `armv7emsp`                                   |       ✔️        |        ✔️        | 🔷                | `natmod` job, `arch: armv7emsp` (where EXTRA_FEAT is set); usermod explicitly excluded — MICROBIT overflows flash, nRF52840 boards either need a Bluetooth softdevice or hit an LTO bug in gcc-arm-none-eabi                                                                                                     |
| mimxrt                     | `armv7emsp`, `armv7emdp`                      |       ✔️        |        ✔️        | 🔷                | `natmod` job covers both ARCHes; usermod deliberately not added                                                                                                                                                                                                                                                  |
| zephyr (rv32m1_vega_ri5cy) | `rv32imc`                                     |       ✔️        |        ❌        | ➖                | not in CI — no job added yet (unverified)                                                                                                                                                                                                                                                                        |
| qemu                       | depends on emulation target                   |       ✔️        |        ✔️        | 🔶                | `usermod-qemu-armv7m` job — real Cortex-M3 firmware (`BOARD=MPS2_AN385`) under `qemu-system-arm`, driven over the raw REPL by `micropython/ci/run_qemu.py`. The only bare-metal execution test here; `test_a7p_core.py` only, since the port has no writable filesystem |
| cc3200                     | ➖                                             |       ❌        |        ✔️        | ➖                | not in CI — deprecated, native emit disabled by default                                                                                                                                                                                                                                                          |
| alif (M55)                 | `armv7emsp`/`armv7emdp` (Cortex-M55)          |       ✔️        |        ✔️        | ➖                | not in CI — ARCH-compatible in principle, unverified, deliberately not added                                                                                                                                                                                                                                     |
| renesas-ra (M4/M33)        | `armv7emsp`                                   |       ✔️        |        ✔️        | ➖                | not in CI — same story: unverified, deliberately not added                                                                                                                                                                                                                                                       |
| bare-arm / minimal         | ➖                                             |       ❌        |        ✔️        | ➖                | not in CI — demo configs, not real boards                                                                                                                                                                                                                                                                        |
| pic16bit                   | ➖                                             |       ❌        |        ✔️        | ➖                | not in CI — different CPU architecture                                                                                                                                                                                                                                                                           |
| powerpc                    | ➖                                             |       ❌        |        ✔️        | ➖                | not in CI — different CPU architecture                                                                                                                                                                                                                                                                           |
| embed                      | ➖                                             |       ➖        |        ➖        | ➖                | not a standalone port (no own Makefile/CMakeLists) — out of CI permanently                                                                                                                                                                                                                                       |

<!-- END mp.md -->

### Install a released build via `mip`

Pushing a `v*` tag runs `.github/workflows/release.yml`, which builds every
natmod `ARCH` above (by calling `mp-natmod.yml` as a reusable workflow, same
mechanism as [ballistics-lab/micropython-bclibc's own
`release.yml`](https://github.com/ballistics-lab/micropython-bclibc/blob/main/.github/workflows/release.yml))
and publishes a GitHub Release with one `a7p_<arch>.native.mpy` asset per
architecture, plus a `package.json` (see
`scripts/ci/build_micropython_release_assets.py`). Each device picks the
matching variant on its own, via the optional per-entry native-code
compatibility tag schema proposed upstream
([micropython/micropython#19532](https://github.com/micropython/micropython/pull/19532),
[micropython/micropython-lib#1144](https://github.com/micropython/micropython-lib/pull/1144);
see the discussion at
[micropython/micropython#19479](https://github.com/micropython/micropython/issues/19479)).

**Until that lands upstream**, the `mip` already on your device (frozen into
stock firmware, or a stock `mpremote`) doesn't understand the tagged `urls`
entries in this `package.json` yet and will raise `ValueError: too many
values to unpack`. Bootstrap a patched `mip` first --
[`micropython/tools/nmip.py`](tools/nmip.py) is a drop-in copy of the
micropython-lib#1144 branch, installed under a different name (`nmip`) so it
doesn't collide with (and doesn't touch) the frozen `mip` module already on
the device:

```python
>>> import mip
>>> mip.install("github:o-murphy/a7p/micropython/tools/nmip.py")
Downloading github:o-murphy/a7p/micropython/tools/nmip.py to /home/murphy/.micropython/lib
Copying: /home/murphy/.micropython/lib/nmip.py
Done
>>> import nmip as mip
>>> mip.install("https://github.com/o-murphy/a7p/releases/download/v1.2.1")
Installing https://github.com/o-murphy/a7p/releases/download/v1.2.1/package.json to /home/murphy/.micropython/lib
Copying: /home/murphy/.micropython/lib/a7p.mpy
Done
```

**Once the upstream PRs are merged and shipped in a MicroPython release**,
plain `mip` (on-device) and `mpremote` (from the host) will handle this
directly -- no bootstrap needed:

```bash
mpremote mip install https://github.com/o-murphy/a7p/releases/download/vX.Y.Z/package.json
```

```python
# or on-device:
import mip

mip.install("https://github.com/o-murphy/a7p/releases/download/vX.Y.Z/package.json")
```

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
only reads whichever one matches its own build system. It also provides a
`manifest.py` that freezes `src/a7p.py` into the firmware image itself (see
"Freezing `a7p.py` into the firmware" below) -- so, unlike an early version
of this doc claimed, a fully self-contained build *is* one extra flag, not
a required post-flash file copy. Point `USER_C_MODULES` at it as one extra
flag on the build command you'd already run for that port:

```sh
git clone https://github.com/micropython/micropython
cd micropython && git submodule update --init --recursive

# Make-based ports (unix, stm32, samd, nrf, mimxrt, esp8266, ...): point
# USER_C_MODULES at the *directory* -- it globs */micropython.mk one level
# down, so this must be the parent of usermod/a7p/, not that directory itself.
cd ports/unix
make USER_C_MODULES=/path/to/a7p/micropython/usermod

# CMake-based ports (rp2, esp32): point USER_C_MODULES at the aggregator
# .cmake file directly instead. rp2's/esp32's own top-level Makefile is a
# thin wrapper around cmake (forwards USER_C_MODULES to it as
# -DUSER_C_MODULES=...) -- `make BOARD=... USER_C_MODULES=...` is the real
# command upstream's own CI uses, not a raw `cmake -B build -D...` invocation.
cd ports/rp2
make BOARD=RPI_PICO_W submodules   # first time only, fetches pico-sdk etc.
make BOARD=RPI_PICO_W USER_C_MODULES=/path/to/a7p/micropython/usermod/micropython.cmake

# webassembly -- the one port natmod categorically can't reach (no WASM
# ARCH in dynruntime.mk), so this is the actual usermod target CI builds.
# VARIANT=pyscript, not the default `standard` variant: `standard` (-s
# ASYNCIFY) is broken against modern emsdk releases -- see
# https://github.com/micropython/micropython/issues/19380. pyscript
# doesn't use ASYNCIFY and isn't affected.
cd ports/webassembly
make VARIANT=pyscript submodules   # first time only, fetches micropython-lib
make VARIANT=pyscript USER_C_MODULES=/path/to/a7p/micropython/usermod
```

That builds the `_a7p` C half straight into the firmware. `a7p.py` (the pure
-Python wrapper `import a7p` actually resolves to) still needs to end up
somewhere Python can find it -- two ways to do that, pick one:

* **Copy it onto the filesystem after flashing** (`mpremote cp
  micropython/src/a7p.py :`) -- zero extra build-time flags, works on every
  port, but is a separate step you repeat after every reflash.
* **Freeze it into the same firmware image** (see "Freezing `a7p.py` into
  the firmware" right below) -- one extra flag on the same build command,
  no post-flash step at all, `import a7p` just works immediately.

### Freezing `a7p.py` into the firmware

MicroPython supports freezing plain `.py` files into the firmware image
(`FROZEN_MANIFEST`, the same mechanism every port already uses for its own
stdlib/board-specific modules) -- `micropython/usermod/manifest.py` is a
one-line fragment that freezes `src/a7p.py` this way. It's a fragment, not a
complete manifest by itself: `FROZEN_MANIFEST` takes exactly one file, and
every port already points it at a default manifest that freezes required
stuff (`asyncio`, per-board extras) -- pointing `FROZEN_MANIFEST` straight at
`usermod/manifest.py` instead would silently drop all of that. Write a small
custom manifest that `include()`s both, and pass FROZEN_MANIFEST at it
alongside `USER_C_MODULES`:

```sh
cat > my_manifest.py <<'EOF'
include("$(PORT_DIR)/boards/manifest.py")   # this port's own default -- see the
                                             # table below, it isn't always this path
include("/path/to/a7p/micropython/usermod/manifest.py")
EOF

cd ports/rp2
make BOARD=RPI_PICO_W \
     USER_C_MODULES=/path/to/a7p/micropython/usermod/micropython.cmake \
     FROZEN_MANIFEST=/path/to/my_manifest.py
```

Each port's own default manifest path (checked directly against that port's
`Makefile`, not assumed -- this is the `$(PORT_DIR)/...` half of the
`include()` above):

| Port | Default manifest |
| --- | --- |
| `unix` (`standard` variant) | `variants/standard/manifest.py` |
| `nrf` | `modules/manifest.py` |
| `rp2`, `esp32`, `stm32`, `samd`, `mimxrt` | `boards/manifest.py` |

CI (`.github/workflows/mp-usermod.yml`) does exactly this for every
`usermod` matrix entry -- it's not just a documented recipe, it's built and
(for `unix`) run on every push.

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

`esp8266` is mechanism-supported (it's in the "Supported" list above -- its
`Makefile` includes `py/py.mk` like any other Make-based port) but
deliberately isn't in this project's CI matrix: the stock `ESP8266_GENERIC`
firmware is already tight enough on IRAM that adding this module's code via
a full usermod rebuild overflows `iram1_0_seg`. That's a genuine
flash/memory constraint of that board's stock config, not a defect in this
module -- `natmod` (see `natmod/build/xtensa/`) is the mechanism that
actually fits on that chip, since it's a standalone `.mpy` copied onto
already-flashed stock firmware rather than more code baked into the same
image. A board with a roomier partition table (a custom `ESP8266_GENERIC`
variant with a bigger IRAM/flash budget) would likely still build fine via
usermod; this just isn't true of the stock config CI builds against.

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

Verified end-to-end in CI (`.github/workflows/mp-usermod.yml`, `usermod`
job), three targets, all genuinely natmod-can't-reach cases:

* `webassembly` (`VARIANT=pyscript`) builds with `USER_C_MODULES` + a
  combined `FROZEN_MANIFEST` (freezing `a7p.py` per the section above) with
  no manual patching, and runs the full test suite (`tests/test_a7p_core.py`,
  `tests/test_a7p.py`, `tests/test_validate.py` -- `load`/`dump` included,
  see "No firmware hashlib.md5 dependency" below for why that's no longer
  the pyscript-only-gets-a-subset case it used to be) against the built
  `micropython.mjs` via a small Node harness (`tests/run_wasm_tests.mjs`)
  that drives the wasm build's own `loadMicroPython`/`runPython` JS API --
  a genuine functional run (decode, mutate through `uctypes`, re-encode,
  validate), not just a build check, since `webassembly` can actually
  execute in the CI runner itself.
* `unix` on `aarch64`, on a GitHub-hosted `ubuntu-24.04-arm` runner (free on
  public repos, GA since August 2025) -- no cross-compiler or Docker, just a
  native build on real ARM64 hardware, the same way the natmod job's x64
  unix build already runs on `ubuntu-latest`. `dynruntime.mk` has no
  aarch64 ARCH at all, so natmod is impossible here regardless of runner;
  runs the full suite -- `tests/test_a7p.py`/`tests/test_validate.py`,
  `load`/`dump` included.
* `windows` on `x86`/`x64`, on `windows-latest` via MSYS2's plain
  MINGW32/MINGW64 environments -- `mpconfigport.h` disables
  `MICROPY_EMIT_X64`/`THUMB` outright, so natmod is impossible on `windows`
  regardless of architecture. Same unprefixed-gcc recipe upstream's own
  `build-mingw` CI job uses (see
  `micropython/.github/workflows/ports_windows.yml`) -- a recompile of an
  already-proven recipe, not a first attempt.
* `windows` on `arm64`, on `windows-11-arm` via MSYS2's `CLANGARM64`
  environment. This was tried once and dropped, because upstream MicroPython
  doesn't test Windows ARM64 at all and each failure (a missing
  `set_fmode_binary`, then `strip`, then `size`, then `windres`) cost a full
  CI round-trip of guesswork. A proven reference exists now --
  o-murphy/micropython-wasm3 runs the same combination green -- and it both
  confirms those earlier fixes and shows `windres` never needed one, only an
  empty `CROSS_COMPILE`.
* `unix` on `armhf`/`mipsel`, cross-compiled -- the build recipe directly
  mirrors upstream MicroPython's own `tools/ci.sh` `ci_unix_qemu_arm_*` (also
  proven working for this project's own module by a real CI run). Only
  `mipsel` still *runs* under `qemu-user-static`: `armhf` moved to
  `ubuntu-24.04-arm`, which executes 32-bit ARM on its own CPU (measured on
  the runner, not assumed), and switched to `gnueabihf` to match -- soft-float
  `gnueabi` baselines at ARMv5TE, whose SWP atomics ARMv8 removed. Two further
  deltas from upstream are deliberate: `LDFLAGS_EXTRA=-static` (deployability,
  same reasoning as micropython/micropython#17456) and `mipsel` substituted
  for upstream's own big-endian
  `mips` choice: this module's zero-copy design hardcodes
  `uctypes.LITTLE_ENDIAN` (`a7p.py`) over memory nanopb populates in the
  host's native byte order, so a genuinely big-endian host produces wrong
  values, not a crash -- confirmed directly (build and QEMU run both
  succeeded on `mips`, but `test_a7p.py`'s zero_x/zero_y/sc_height assertion
  failed). Every real deployment target this project supports is
  little-endian, so this isn't a real-world gap; `mipsel` is proven working
  end-to-end by ballistics-lab/micropython-bclibc's own CI.

**Not done: musl for those two static builds.** `armhf` and `mipsel` link
`-static` against glibc, and glibc warns on every such link that `dlopen` and
`getaddrinfo` still need the shared libraries from the glibc they were linked
against — so a "static" glibc binary is not actually self-contained on the
minimal target it exists for. That is also half the reason the `aarch64` row
stopped linking static. musl has no NSS and a stub `dlopen`, so the same build
has neither caveat. Measured rather than assumed: a musl static build came back
with **zero** link warnings against glibc's two, `ldd` reporting `not a dynamic
executable`, and `getaddrinfo` working, at the cost of `MICROPY_PY_BTREE=0` and
`MICROPY_PY_FFI=0`. Deliberately not implemented for now; recorded so the
measurement is not lost.

Per the natmod-first policy above, `stm32`, `samd`, `mimxrt`, `esp8266` and
`nrf` are intentionally **not** in the `usermod` CI job -- natmod already
covers all of them (see the ARCH table earlier in this file), so a usermod
build there would just be a slower, more expensive way to verify what natmod
already verifies.

`unix` on `x64`/`x86`, `rp2` and `esp32` used to be on that list and are not
any more, each for its own reason. The two unix rows because a usermod links
against the port's own libc and lives in firmware `.bss` while a natmod links
against dynruntime and carries its own -- a green natmod says nothing about
the usermod path on the same machine. `esp32` because a natmod only borrows
the xtensa compiler out of ESP-IDF, while a usermod has to survive IDF's own
components and the port's flash/IRAM budget. And `rp2` for the strongest
reason of the three: `mp-natmod.yml` *builds* `armv6m` and never runs it, so
until `usermod-rp2040` landed, nothing in this project had ever executed on
an RP2040, emulated or otherwise.

The mechanism still works on
every one of them (`USER_C_MODULES` + `FROZEN_MANIFEST`, exactly as
documented above) if you build it yourself; it's just not exercised by this
project's own CI. Two ports are worth calling out for board-level nuance if
you do:

* `nrf`: `MICROBIT` (nRF51822, 256KB flash) overflows `FLASH_TEXT` once
  `a7p.py` and this module's C code are added on top of its own defaults --
  the same flash-budget story as `esp8266`'s stock firmware. The roomier
  nRF52840 boards either need an extra out-of-band Bluetooth softdevice
  download (`ARDUINO_NANO_33_BLE_SENSE`) or hit a pre-existing GCC/LTO
  toolchain bug unrelated to this module (`PCA10056`: `lto1: sorry,
  unimplemented: Thumb-1 'hard-float' VFP ABI`, reproduced locally against
  the pinned `v1.28.0` + Ubuntu's `gcc-arm-none-eabi`, persists with
  `LTO=0`).
* `esp8266`: the flash budget is the *second* problem. The first is that
  `ports/esp8266/posix_helpers.c:35` implements `malloc` as `gc_alloc`, while a
  usermod's globals live in firmware `.bss`, which `gc_collect()` never scans --
  so anything allocated at import time is unreachable to the collector and free
  to be reused. That is not a build error and not an immediate crash; it is
  wrong answers later. `MP_REGISTER_ROOT_POINTER` is the prerequisite, and the
  hard part of it is that MicroPython's GC only traces block-aligned pointers.
  This module does not allocate in C, so it is not affected today -- but treat
  the port as unsafe for usermods in general rather than merely flash-tight.
  `stm32`, `samd`, `nrf`, `alif`, `zephyr` and `cc3200` have no C heap at all.
* `stm32`: some tiny-flash boards (`NUCLEO_F091RC` among them) set
  `FROZEN_MANIFEST` empty in their own `mpconfigboard.h` ("MCU is tight on
  flash space") -- forcing one on anyway also skips that board's
  `micropython-lib` submodule fetch (gated on `FROZEN_MANIFEST` being
  non-empty at `make submodules` time) and breaks the build. Pick a
  roomier board (e.g. `NUCLEO_H743ZI`) if you hit this.

## Usage

```python
import a7p

with open("MyProfile.a7p", "rb") as fp:
    profile = a7p.load(fp)  # or a7p.loads(data) from raw bytes

print(profile.get_str("profile_name"))
print(profile.profile.zero_x, profile.profile.sc_height)

# direct, zero-copy field access -- no re-decode needed to see writes
profile.profile.zero_x = 100
profile.profile.distances[0] = 5000
profile.profile.switches[0].zoom = 2
profile.set_str("profile_name", "My Profile")

with open("MyProfile_edited.a7p", "wb") as fp:
    a7p.dump(profile, fp)  # or data = a7p.dumps(profile)
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

### No firmware `hashlib.md5` dependency

`load`/`loads`/`dump`/`dumps` need an md5 digest for the `.a7p` file
format's 32-byte hex prefix. Earlier versions of this module called
`hashlib.md5` for that, which broke on firmware built with
`MICROPY_PY_SSL` off (common on flash-constrained embedded targets, since
`MICROPY_PY_HASHLIB_MD5` defaults to whatever `MICROPY_PY_SSL` is set to --
`py/mpconfig.h`) with `AttributeError: module 'hashlib' has no attribute
'md5'`, even though `hashlib` itself (a separate, lower flag,
`MICROPY_PY_HASHLIB`) was present.

This module now vendors its own md5 (`src/md5.c`/`md5.h`, the public-domain
implementation by Solar Designer/Alexander Peslyak, the same one used by
PHP core, ClamAV, FreeType, Dovecot, and others -- see the file header for
provenance/license) and exposes it as `_a7p._md5()`, so `load`/`dump` no
longer depend on the target firmware's `hashlib`/`MICROPY_PY_SSL`
configuration at all. `Profile.decode`/`.encode`/`.validate` never touched
`hashlib` either way -- they work on the raw protobuf body.

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
profile.profile.sc_height = 999999  # decodes/encodes fine, structurally valid
profile.validate()  # raises A7PValidationError: "sc_height: out of range"
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

`Profile.clamp()` is `validate()`'s counterpart for fixing rather than just
reporting: it walks the same fields/thresholds and pulls any out-of-range
value back into bounds in place, returning how many it changed (0 if
nothing needed it):

```python
profile.profile.sc_height = 999999
profile.clamp()  # -> 1
profile.profile.sc_height  # -> 5000 (A7P_SC_HEIGHT_MAX)
```

It's independent of `validate()` -- call either on its own, or `clamp()`
then `validate()` if you want both. It deliberately does *not* try to fix
everything `validate()` can flag: structural rules a number can't resolve
by clamping (`coef_rows` below its minimum item count, duplicate
`coef_rows[].mv`) are left alone, and `distances[0] == 0` is skipped for the
same real-world-data reason described above (clamping it up to 100 would
silently rewrite legitimate files). `a7p_clamp()` (`src/a7p_validate.c`)
shares its bounds with `a7p_validate()` -- same generated
`src/a7p_validate.h`, no separate source of truth to keep in sync.

## Running the tests

```sh
cd micropython/natmod && make MPY_DIR=/path/to/micropython ARCH=x64 dist
cd ../..
MICROPYPATH=micropython/natmod/build/x64 /path/to/micropython/ports/unix/build-standard/micropython micropython/tests/test_a7p.py

cd go/assets
MICROPYPATH=../../micropython/natmod/build/x64 /path/to/micropython/ports/unix/build-standard/micropython ../../micropython/tests/test_validate.py
```
