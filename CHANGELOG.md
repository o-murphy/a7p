# Changelog

All notable changes to the `a7p` packages (`py`, `js`, `dart`) are
documented together in this one file — the single source of truth for all
three, including their pre-monorepo history (`js` as `o-murphy/a7p-js`,
`dart` as `o-murphy/a7p-dart`; `py` had no `CHANGELOG.md` of its own).
`py/CHANGELOG.md`, `js/CHANGELOG.md`, and `dart/CHANGELOG.md` are
**generated** from this file by `scripts/ci/sync_changelogs.py` (each
package registry — pub.dev, and generally npm/PyPI too — expects to find
one in the published package). **Edit this file, then run
`scripts/ci/sync_changelogs.py` and commit the regenerated
`py/`/`js`/`dart/CHANGELOG.md` alongside your change.**

From this repo's own first release onward, one version tag drives a
release across all three packages together (see
`.github/workflows/release.yml`) — but not every package necessarily
changed in every release, so a version heading below may have only some of
`### py/`, `### js/`, `### dart/`. Versions before that point are each
package's own independent pre-merge history — `js` and `dart` had entirely
unrelated version numbers and release schedules back then (e.g. `js`'s
`[1.1.0]` and `dart`'s `[0.1.0]` are unrelated releases that happened to
land close together), so a heading below only ever has one package's
subsection until the monorepo's own version numbers start.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
