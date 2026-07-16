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
