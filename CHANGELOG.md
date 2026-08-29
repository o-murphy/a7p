# Changelog

All notable changes to the `a7p` packages (`py`, `js`, `dart`, `go`) are
documented together in this one file — the single source of truth for all
four, including their pre-monorepo history (`js` as `o-murphy/a7p-js`,
`dart` as `o-murphy/a7p-dart`, `go` as `o-murphy/a7p-go`; `py` had no
`CHANGELOG.md` of its own). `py/CHANGELOG.md`, `js/CHANGELOG.md`,
`dart/CHANGELOG.md`, and `go/CHANGELOG.md` are **generated** from this file
by `scripts/ci/sync_changelogs.py` (each package registry — pub.dev, and
generally npm/PyPI too — expects to find one in the published package;
`go get`/pkg.go.dev don't strictly require one, but `go/` carries one too
for consistency with the other three). **Edit this file, then run
`scripts/ci/sync_changelogs.py` and commit the regenerated
`py/`/`js`/`dart/`/`go/CHANGELOG.md` alongside your change.**

`micropython/` is documented here too (`### micropython/`, same as the four
packages above) but isn't synced to a package-local `CHANGELOG.md` by
`scripts/ci/sync_changelogs.py` — it doesn't publish to a package registry
(PyPI/npm/pub.dev/pkg.go.dev), only as GitHub Release assets (see
`.github/workflows/release.yml`'s `publish-micropython` job), so there's no
registry-facing file that would need one.

From this repo's own first release onward, one version tag drives a
release across all four packages together (see
`.github/workflows/release.yml`) — but not every package necessarily
changed in every release, so a version heading below may have only some of
`### py/`, `### js/`, `### dart/`, `### go/`. Versions before that point are
each package's own independent pre-merge history — `js`, `dart`, and `go`
had entirely unrelated version numbers and release schedules back then
(e.g. `js`'s `[1.1.0]` and `dart`'s `[0.1.0]` are unrelated releases that
happened to land close together), so a heading below only ever has one
package's subsection until the monorepo's own version numbers start.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### micropython/

#### Added

- New `micropython/` module (experimental): a MicroPython native module
  exposing `.a7p` decode/encode/validate/clamp, with zero-copy field access
  via `uctypes` — see `micropython/README.md`. Two build paths sharing the
  same C/Python sources: `natmod/` (standalone `.mpy`, no firmware rebuild)
  and `usermod/` (compiled into the firmware image, for ports/architectures
  natmod can't reach — `webassembly`, `unix` on `aarch64`, `windows`, `unix`
  on `armhf`/`mipsel`).
- CI: `.github/workflows/mp-natmod.yml` and `.github/workflows/mp-usermod.yml`
  build and test every supported port/architecture on each push.
- Release: `.github/workflows/release.yml` now also builds every natmod
  `ARCH` and publishes one `a7p_<arch>.native.mpy` asset per architecture
  plus a `package.json` (per-entry native-code compatibility tags) to the
  GitHub Release, so `mip`/`mpremote mip install` can pick the right
  variant per device — see `scripts/ci/build_micropython_release_assets.py`
  and `micropython/tools/nmip.py` (bootstrap for the tagged-`urls` format,
  until the upstream `mip` support for it ships).
- CI: the `usermod` matrix now also covers `unix` on `x64`/`x86`, and two new
  jobs cover `esp32` (`BOARD=ESP32_GENERIC`, ESP-IDF v5.5.1, **build-only** —
  there is no esp32 emulator to run a firmware image on) and `rp2040`
  (`BOARD=RPI_PICO`, built **and run** under the
  [rp2040py](https://github.com/o-murphy/rp2040py) emulator via
  `micropython/ci/run_rp2040py.py`). All four go against the natmod-first
  policy deliberately: the two unix rows because a usermod links against the
  port's own libc while a natmod links against dynruntime, `esp32` because a
  usermod must survive IDF's own components and the port's flash/IRAM budget,
  and `rp2040` because `mp-natmod.yml` builds `armv6m` without ever running
  it — that job is the first time anything here has executed on an RP2040.
- CI: `natmod` now *executes* `armv7emsp` and `armv7emdp`, not just builds
  them, on a 32-bit armhf `ports/unix` host on `ubuntu-24.04-arm` — real ARM
  silicon, no emulator. `py/persistentcode.h`'s `MPY_FEATURE_ARCH_TEST` is a
  range (`ARMV6M <= x <= ARMV7EMDP`) rather than an equality, so a Cortex-M
  `.mpy` loads on such a host. `armv6m`/`armv7m` cannot join them: they are
  built soft-float, so their floats reach the runtime in core registers while
  an armhf host reads them from VFP registers, and the `.mpy` loads and then
  returns wrong values rather than failing.

#### Changed

- CI: every `ballistics-lab/micropython-native-ci` action reference (both
  `mp-natmod.yml` and `mp-usermod.yml`) is now pinned to the `v0.2.0` tag
  instead of a mix of the `v0.1.0` tag (`fetch-/clone-micropython`,
  `build-natmod-arch`) and the `claude/usermod-shared-action-kwulzv`
  development branch (everything added this cycle). `build-natmod-arch`
  also drops its `-arch` suffix (`build-natmod`) now that a tag past that
  rename exists. No behavior change: `v0.2.0` is exactly what that branch
  contained, squash-merged.
- CI: `usermod-qemu-armv7m`, `usermod-esp32`, and `usermod-rp2040` now check
  out MicroPython via `micropython-native-ci`'s `fetch-micropython` instead
  of a plain `actions/checkout` -- matching what every other job in this
  workflow already does, and what bclibc/wasm3 already do for the same
  three ports. Each job's own now-unnecessary manual submodule-init step
  (a `make ... submodules` or raw `git submodule` invocation, needed only
  because MicroPython came from a git checkout) is gone with it.
  `usermod-rp2040` originally switched to `clone-micropython` +
  `pico_sdk_submodules: "true"` instead (see below for why plain
  `fetch-micropython` turned out to be enough there too).
- CI: the `usermod-cross` (`armhf`/`mipsel`) job now builds `VARIANT=standard`
  instead of upstream's own `VARIANT=coverage`, matching every other unix row
  in `mp-usermod.yml` (`x64`/`x86`/`aarch64` all already build standard).
  `coverage` broadens upstream's own `tools/ci.sh` CI surface across their
  whole matrix; nothing about armhf/mipsel specifically needs it here, and
  the mismatch against this workflow's other rows was inherited from a
  straight port of the upstream recipe rather than a deliberate choice.
  `FROZEN_MANIFEST` now combines with `variants/standard/manifest.py`
  instead, same as the x64/x86/aarch64 rows.
- CI: `mp-usermod.yml`'s unix rows (`x64`/`x86`/`aarch64`/`armhf`/`mipsel`)
  and Windows rows (`x86`/`x64`/`arm64`) no longer carry their own
  apt/cross-compile/deplibs/MSYS2 recipe inline — both now call
  `build-usermod-unix`/`build-usermod-windows` from
  [`ballistics-lab/micropython-native-ci`](https://github.com/ballistics-lab/micropython-native-ci),
  the same repo `mp-natmod.yml` already used for `build-natmod`.
  `micropython/` is checked out via that repo's `clone-micropython` action
  now too, for the same reason `mp-natmod.yml` already did — the shared
  actions need `MPY_DIR` exported, which a plain `actions/checkout` never
  did. No behavior change: manifests, `USER_C_MODULES` paths, and every
  build output land exactly where they did before.
- CI: the `usermod` `armhf` row runs on `ubuntu-24.04-arm` instead of under
  `qemu-user`. A GitHub arm64 runner executes 32-bit ARM on its own CPU —
  measured on the runner rather than assumed — so the binary is cross-built
  there and then run natively. That is also why it switched from upstream's
  soft-float `gnueabi` to `gnueabihf`: `armel` baselines at ARMv5TE, whose
  SWP atomics ARMv8 removed outright. `mipsel` is still emulated; GitHub has
  no mips runner.
- CI: the `usermod` `aarch64` row is a plain dynamic build again, dropping
  `MICROPY_STANDALONE=1 LDFLAGS_EXTRA=-static`. It runs natively on the
  machine that builds it, `release.yml` deliberately does not publish
  `mp-usermod.yml`'s artifacts, and a static glibc's `dlopen` still needs the
  matching shared libraries at run time — so the static link cost an extra
  toolchain set and a libffi-from-source pass while buying nothing. `armhf`
  and `mipsel` keep it, where it is what lets the binary start at all.
- CI: the `usermod` `webassembly` row's emsdk-install/mpy-cross/port-build
  steps are now `build-usermod-webassembly` from
  [`ballistics-lab/micropython-native-ci`](https://github.com/ballistics-lab/micropython-native-ci),
  same as the unix/Windows rows above. The row's own "Fetch port submodules"
  step (needed because `micropython/` here comes from `clone-micropython`,
  a shallow clone with no submodules, not a release tarball) stays
  caller-side and now runs without first sourcing `emsdk/emsdk_env.sh` —
  that target is `py/mkrules.mk`'s generic `submodules` rule, a plain `git
  submodule update --init`, and never touched `emcc`; the sourcing was only
  ever incidental to "Install emsdk" having previously run as the step
  right before it. No behavior change: `VARIANT=pyscript`, `emsdk latest`,
  and the combined FROZEN_MANIFEST step stay exactly what they were.
- CI: `usermod-rp2040`'s checkout simplified again, this time to plain
  `fetch-micropython` — the `clone-micropython` + explicit submodule list
  + `pico_sdk_submodules: "true"` from the entry above was itself never
  required. The "Cannot find source file:
  .../lib/mbedtls/library/aes.c" failure that originally justified it was
  against an *incomplete* `clone-micropython` `submodules:` value (missing
  `lib/mbedtls`), not evidence a git clone was ever needed — the release
  tarball already vendors every `lib/` this port's `CMakeLists.txt` needs.
  `pico_sdk_submodules` was never load-bearing either:
  `ports/rp2/CMakeLists.txt` redirects
  `PICO_TINYUSB_PATH`/`PICO_LWIP_PATH`/`PICO_BTSTACK_PATH`/
  `PICO_CYW43_DRIVER_PATH` at `${MICROPY_DIR}/lib/<name>` (MicroPython's
  own top-level submodules) rather than pico-sdk's own nested vendored
  copies, so pico-sdk's internal submodule tree is never actually touched.
  Proven, green, on `o-murphy/micropython-wasm3`'s rp2 row and
  `ballistics-lab/micropython-bclibc`'s own rp2040 job first.
- CI: `usermod-rp2040`'s toolchain-install/mpy-cross/port-build steps are
  now `build-usermod-rp2040` from
  [`ballistics-lab/micropython-native-ci`](https://github.com/ballistics-lab/micropython-native-ci),
  same as the unix/Windows/webassembly rows above. `build_dir:
  build-RPI_PICO` keeps the resulting path exactly where the Run
  tests/Upload build steps already expect it (`$MPY_DIR/ports/rp2/build-RPI_PICO`),
  same as the plain `make` invocation this replaces, which never passed
  `BUILD=` either.
- CI: `usermod-qemu-armv7m`'s toolchain-install/mpy-cross/port-build steps
  are now `build-usermod-armv7m` from the same
  [`ballistics-lab/micropython-native-ci`](https://github.com/ballistics-lab/micropython-native-ci)
  repo (named after the target architecture, not the QEMU test mechanism
  -- see that action's own header). `qemu-system-arm`/`pyserial` stay
  caller-side: neither is a build dependency (QEMU only runs the
  resulting firmware), same split `build-usermod-rp2040` uses for the
  rp2040py emulator. `build_dir: build-MPS2_AN385` keeps the resulting
  path exactly where Run tests/Upload build already expect it.
- CI: `usermod-esp32`'s ESP-IDF-install/mpy-cross/port-build steps are now
  `build-usermod-esp32` from the same
  [`ballistics-lab/micropython-native-ci`](https://github.com/ballistics-lab/micropython-native-ci)
  repo. `source esp-idf/export.sh` and the port build stay in the
  action's same step (export.sh's env doesn't survive a composite action
  step boundary). No `BUILD=` override: a real CI failure on
  `ballistics-lab/micropython-bclibc`'s own first run showed that passing
  it explicitly -- even set to the port's own default value -- makes
  esp32's internal CMake-driven `mpy-cross` sub-build pick up
  `FROZEN_MANIFEST` through `MAKEFLAGS` and fail with `undefined
  reference to mp_qstr_frozen_const_pool`; the action always uses
  `build-$(BOARD)` now, exactly what Upload build already expects. This
  job also gains a "Dump IDF build logs on failure" diagnostic for free.
- CI: every `ballistics-lab/cibuildmp` reference (`mp-natmod.yml`'s own
  `cibuildmp`/`clone-micropython` steps and every `clone-/fetch-micropython`
  and `build-usermod-*` step in `mp-usermod.yml`) is repinned off the stale
  `v0.3.0` tag, which predates cibuildmp's own config-schema rewrite
  (records 0051/0052): the `[natmod]` table is now rejected outright, and
  `micropython =`/`archs =` no longer exist as config keys at all —
  `build`/`skip` glob against the real `mpy{abi}-{tag}-{arch}` identifier
  instead. `micropython/cibuildmp.toml` drops its `[natmod]` table
  accordingly (`build = "mpy*-v1.28.0-*"` at the top level replaces
  `micropython = "v1.28.0"` + `[natmod] archs = [...]`), and
  `mp-natmod.yml`'s per-arch matrix leg now passes its own `build:` action
  input (`mpy*-${{ env.MPY_REF }}-${{ matrix.arch }}`) instead of the now-
  meaningless `CIBMP_MICROPYTHON`/`CIBMP_ARCHS` env vars. Also drops the
  per-job `gcc-multilib` install for `x86`: natmod is Docker-only as of
  cibuildmp record 0050, so every arch (`x86` included) now builds inside
  cibuildmp's own published natmod image instead of the bare runner. No tag
  past `v0.3.0` exists yet, so every reference is pinned to cibuildmp's own
  current commit SHA in the interim, the same precedent its own tracker
  [0038] already used once before a tag existed — repin to a real tag once
  one is cut. (Superseded for `mp-usermod.yml` by the next entry below: it
  no longer calls the `build-usermod-*` composite actions at all.)
- CI: `mp-usermod.yml` rewritten to build through cibuildmp's own usermod
  platform support (its `feat/usermod` work, part of the same commit
  `mp-natmod.yml` now pins) instead of the low-level `build-usermod-unix`/
  `-windows`/`-webassembly`/`-esp32`/`-rp2040`/`-armv7m` composite actions.
  Every hand-written "Write combined FROZEN_MANIFEST" step and every
  per-port toolchain-install step (MSYS2, apt cross-toolchains, ESP-IDF)
  is gone — `micropython/cibuildmp.toml` gains `manifest =
  "usermod/manifest.py"` and `user-c-modules = "usermod"`, and cibuildmp
  resolves each target (Docker image, manifest combination, toolchain) from
  those two keys the same way `mp-natmod.yml` already does for natmod.
  `windows` is the one structural change beyond a like-for-like swap: all
  three arches now cross-build in one Docker image on `ubuntu-latest` (no
  Windows runner at build time at all), so building and running it are two
  separate jobs now (`usermod-windows-build` → `usermod-windows-test`,
  `windows-latest`/`windows-11-arm`, unchanged) instead of one. `unix`'s
  `x86` row also drops its `MICROPY_FORCE_32BIT=1` override in CI —
  cibuildmp's own `manylinux_2_28_i686` image is genuinely native `i686`,
  not an `-m32` build inside an `x86_64` one; `micropython/README.md`'s own
  per-port table keeps documenting the flag as what a bare-host local build
  (no cibuildmp/Docker) still needs for `x86`, since that stays true
  regardless of what CI does. Every job reads its own build
  straight from cibuildmp's real `ports/<port>/build-<identifier>/` tree
  (pinned to a known path via `CIBMP_CACHE_PATH`, not cibuildmp's own
  `mpyhouse/<identifier>/` copy, which only keeps one file per identifier
  and would drop `webassembly`'s required `.wasm` sibling) rather than a
  workflow-managed `clone-/fetch-micropython` checkout, which this file no
  longer needs at all.

## [1.2.4] - 2026-07-16

### py/

#### Removed

- `yupy` dependency and the hand-written `src/a7p/yupy_schema.py` validator it
  backed — unused by the public `a7p.validate()` path since the migration to
  `schema_validator.py` (`fastjsonschema`/`jsonschema` against
  `schema/a7p.schema.json`), and kept only as a reference/regression suite
  (`tests/test_yupy_schema.py`) until now
- `exceptions.YupyViolation` and `exceptions.A7PYupyValidationError` — folded
  into plain `Violation`/`A7PValidationError`; `A7PValidationError` no longer
  splits errors into `.violations`/`.yupy_violations`/`.all_violations`, just
  one `.violations` list

#### Changed

- CLI flag `--disable-yupy` renamed to `--disable-validator`

### js/

#### Changed

- Regenerated `src/generated/a7p_schema_validator.cjs` via
  `scripts/compile.py` — the only source change was
  `schema/a7p.schema.json`'s `x-decision`/`x-discrepancy` annotation text,
  updated (not dropped) to record in the past tense that `py`'s
  `yupy_schema.py`/`test_yupy_schema.py` (referenced there as context for why
  these bounds were picked) have since been deleted, see `py/` above. These
  `x-*` keys are documentation only, ignored by `ajv` — no validation
  behavior changed.

### dart/

#### Changed

- Regenerated `lib/src/generated/a7p_schema.g.dart` via `scripts/compile.py`
  — same annotation-only `schema/a7p.schema.json` change as `js/` above, no
  validation behavior changed (`x-*` keys are ignored by `json_schema`).

### go/

#### Changed

- Regenerated `a7p/generated/a7p_schema.g.json` via `scripts/compile.py` —
  same annotation-only `schema/a7p.schema.json` change as `js/` above, no
  validation behavior changed (`x-*` keys are ignored by
  `santhosh-tekuri/jsonschema`).

## [1.2.3] - 2026-07-14

`schema/a7p.schema.json`'s required string fields (`profile_name`,
`cartridge_name`, `bullet_name`, `short_name_top`, `short_name_bot`,
`caliber`) wrongly carried `minLength: 1`, rejecting the empty string —
real device profiles ship these unset. Fixed at the source and
regenerated into all four packages via `scripts/compile.py`.

### py/

#### Fixed

- `caliber`, `profile_name`, `cartridge_name`, `bullet_name`,
  `short_name_top`, and `short_name_bot` now accept an empty string,
  matching real device profiles — `_compiled_schema.py` and the bundled
  `a7p.schema.json` regenerated from `schema/a7p.schema.json`

### js/

#### Fixed

- Same `minLength` fix as `py/`, regenerated into
  `src/generated/a7p_schema_validator.cjs`

### dart/

#### Fixed

- Same `minLength` fix as `py/`, regenerated into
  `lib/src/generated/a7p_schema.g.dart`

### go/

#### Fixed

- Same `minLength` fix as `py/`, regenerated into
  `a7p/generated/a7p_schema.g.json`

## [1.2.2] - 2026-07-09

### py/

#### Changed
- Updated dependencies

### dart/

#### No changes since 1.2.1 (patch has been applied to js package)

### js/

#### No changes since 1.2.1 (patch has been applied to js package)

### go/

#### No changes since 1.2.1 (patch has been applied to js package)

## [1.2.1] - 2026-07-09

### py/

#### No changes since 1.2.0 (patch has been applied to js package)

### dart/

#### No changes since 1.2.0 (patch has been applied to js package)

### js/

#### Fixed

- `ajv` moved from `devDependencies` to `dependencies` — the compiled
  standalone validator (`src/generated/a7p_schema_validator.cjs`) calls
  `require("ajv/dist/runtime/ucs2length")` at runtime (ajv's standalone
  codegen emits this for unicode-safe string length checks), so `ajv` must
  ship with the package, not just be available at build time. Consumers
  installing `a7p-js` without `ajv` already present elsewhere in their tree
  hit `Cannot find module 'ajv/dist/runtime/ucs2length'` (e.g. under
  Metro). The `1.2.0` changelog entry below claiming "`ajv` is a
  devDependency only (used by the codegen script, not shipped)" was wrong.

### go/

`go` merged from `o-murphy/a7p-go` into this monorepo, with full git
history preserved — see `docs/DESIGN-schema-unification.md` for the design
behind this merge.

#### Changed

- Validation now runs against the shared `schema/a7p.schema.json` via
  `schema_validator.go` (`github.com/santhosh-tekuri/jsonschema/v6`,
  compiled once into a lazy singleton) instead of the vendored
  `protovalidate-go`/`go-playground/validator` checks
- `proto/profedit.proto` now lives once at the repo root instead of a
  vendored copy (with `buf`/`protovalidate` annotations) under
  `a7p/profedit/`; the unused `buf`/`protovalidate` toolchain and
  `protoc-gen-go-grpc` codegen (the proto defines no `service`) are gone
- `go.mod`'s module path is now `github.com/o-murphy/a7p` (was the
  non-resolvable `a7p-go`), with `go.mod`/`go.sum` at the repo root so this
  module shares the same `vX.Y.Z` release tag as `py`/`js`/`dart` instead of
  needing its own subdirectory-prefixed `go/vX.Y.Z` tags

## [1.2.0] - 2026-07-08

`py`, `js`, and `dart` merged from separate repos/submodules into this
monorepo, with full git history preserved — see
`docs/DESIGN-schema-unification.md` for the design behind this release.

### py/

#### Changed

- Validation now runs against the shared `schema/a7p.schema.json` via
  `schema_validator.py` (`fastjsonschema`-compiled, `jsonschema` fallback
  for full error lists) instead of the hand-written `yupy_schema.py`
  (kept temporarily, unused by the public API, as a reference/safety net)
- `proto/profedit.proto` now lives once at the repo root instead of a
  local copy under `proto/`

### js/

#### Changed

- Validation now runs against the shared `schema/a7p.schema.json` via a
  compiled, standalone `ajv` validator (`src/generated/a7p_schema_validator.cjs`,
  regenerated by `scripts/build_schema_validator.mjs`) instead of `yup` —
  `yup` and `@types/yup` are gone; `ajv` is a devDependency only (used by
  the codegen script, not shipped)
- `proto/profedit.proto` now lives once at the repo root instead of a
  local copy under `src/proto/`
- License changed from ISC to LGPL-3.0, matching `dart` — both generate
  bindings from the same LGPL-3.0-sourced `proto/profedit.proto`

#### Added

- First test suite (`test/validate.test.ts`, 10 tests) covering the same
  categories as `dart`'s validator tests

#### Fixed

- `zoom` was unbounded (accepted 0–255); now bounded to 0–6, matching the schema
- `bc_cd`/`mv` for `CUSTOM` drag models were capped ×10 too low
- `b_length` minimum was 1 instead of 10
- `ValidationError` was imported from `yup`, not this package's own
  `errors.ts` — `error instanceof ValidationError` checks in `index.ts`
  never matched a validation failure as a result; fixed as part of the
  `yup` removal

### dart/

#### Changed

- Validation now runs against the shared `schema/a7p.schema.json` via the
  `json_schema` package instead of hand-written `A7pValidator`/
  `A7pFieldConstraints` range checks — the schema is embedded as a
  generated Dart string constant (`lib/src/generated/a7p_schema.g.dart`,
  regenerated by `python scripts/compile.py --dart`), since no
  standalone-codegen JSON Schema validator exists for Dart
- `c_zero_distance_idx` no longer bounds dynamically by `distances.length -
  1`; now the static 0–255 range, matching `py`/`js`
- `proto/profedit.proto` now lives once at the repo root instead of a
  local copy under `proto/`

#### Added

- Test suite (`test/a7p_validator_test.dart`, 9 tests) covering real
  protobuf `Payload` objects, including the `c_idx` 201–254 gap and `mv`
  uniqueness
- "Dimensions" table in `README.md` (previously missing, unlike `py`/`js`)

## [0.1.0] - 2026-07-05

### dart/

First stable release, no changes from [0.1.0-beta.1](#010-beta1---2026-07-04).

## [0.1.0-beta.1] - 2026-07-04

### dart/

#### Added

- `A7pFile` — `.a7p` binary format encode/decode (`[32-byte MD5 hex string][protobuf bytes]`)
- `A7pValidator` — profile field validation
- `A7pFieldConstraints` — per-field raw wire scale (`fractionDigits`) and
  independent UI display precision (`uiFractionDigits`)
- Generated protobuf bindings (`lib/src/proto/`) from `proto/profedit.proto`
- `bin/generate_proto.dart` — regenerates the protobuf bindings; cross-platform
  replacement for the shell-based `protoc` invocation used in the original
  monorepo Makefile
- Test suite (`test/a7p_field_constraints_test.dart`)
- CI workflow (`.github/workflows/ci.yml`): analyze, format check, test
  (Linux/macOS/Windows), pub.dev dry-run jobs

Initial extraction from `archerbc2_flutter/packages/a7p` into a standalone
package.

## [1.1.0] - 2026-06-12

### js/

#### Changed

- Replaced `protobufjs` runtime with `@bufbuild/protobuf` via `ts-proto`
- Proto types are now generated as TypeScript (`src/profedit.ts`) — no separate copy step
- `build:proto` now uses `protoc` + `ts-proto` instead of `pbjs`/`pbts`
- Removed `build:copy` step and `fix-imports.mjs` script
- Fixed `tsconfig.json` for TypeScript 6: explicit `rootDir`, `moduleResolution: bundler`
- Fixed `exports` field: `types` before `import`, `"./*"` glob pattern

#### Removed

- `profedit` namespace re-export from main entry point (import from `a7p-js/profedit` instead)
- `cpy-cli` and `protobufjs-cli` dev dependencies

## [1.0.9] - 2025-09-30

### js/

#### Changed

- Updated package exports

## [1.0.8] - 2025-09-23

### js/

#### Changed

- Updated `yup` to v1.7.1
- Updated dependencies

## [1.0.7] - 2025-09-16

### js/

#### Changed

- Updated dependencies
- Updated `build:proto` script

## [1.0.6] - 2025-09-04

### js/

#### Changed

- Updated Babel and Jest dependencies

## [1.0.5] - 2025-09-02

### js/

#### Fixed

- Validation fix for `switches` distance field

## [1.0.4] - 2025-04-28

### js/

#### Changed

- Updated package exports

## [1.0.3] - 2025-04-22

### js/

#### Fixed

- Ranges validation fix

## [1.0.2] - 2025-04-18

### js/

#### Fixed

- Import resolution fix

## [1.0.1] - 2025-04-17

### js/

#### Added

- Initial release

[Unreleased]: https://github.com/o-murphy/a7p/compare/v1.2.4...HEAD
[1.2.4]: https://github.com/o-murphy/a7p/compare/v1.2.3...v1.2.4
[1.2.3]: https://github.com/o-murphy/a7p/compare/v1.2.2...v1.2.3
[1.2.2]: https://github.com/o-murphy/a7p/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/o-murphy/a7p/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/o-murphy/a7p/releases/tag/v1.2.0
