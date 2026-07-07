# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Generated from the repo root's `CHANGELOG.md` (the single source of truth,
including this package's full history — see that file's own header) by
`scripts/ci/sync_changelogs.py` — edit that file, not this one, then
regenerate.

<!-- BEGIN AUTO-GENERATED FROM ROOT CHANGELOG.md -->
## [1.1.0] - 2026-06-12

### Changed

- Replaced `protobufjs` runtime with `@bufbuild/protobuf` via `ts-proto`
- Proto types are now generated as TypeScript (`src/profedit.ts`) — no separate copy step
- `build:proto` now uses `protoc` + `ts-proto` instead of `pbjs`/`pbts`
- Removed `build:copy` step and `fix-imports.mjs` script
- Fixed `tsconfig.json` for TypeScript 6: explicit `rootDir`, `moduleResolution: bundler`
- Fixed `exports` field: `types` before `import`, `"./*"` glob pattern

### Removed

- `profedit` namespace re-export from main entry point (import from `a7p-js/profedit` instead)
- `cpy-cli` and `protobufjs-cli` dev dependencies

## [1.0.9] - 2025-09-30

### Changed

- Updated package exports

## [1.0.8] - 2025-09-23

### Changed

- Updated `yup` to v1.7.1
- Updated dependencies

## [1.0.7] - 2025-09-16

### Changed

- Updated dependencies
- Updated `build:proto` script

## [1.0.6] - 2025-09-04

### Changed

- Updated Babel and Jest dependencies

## [1.0.5] - 2025-09-02

### Fixed

- Validation fix for `switches` distance field

## [1.0.4] - 2025-04-28

### Changed

- Updated package exports

## [1.0.3] - 2025-04-22

### Fixed

- Ranges validation fix

## [1.0.2] - 2025-04-18

### Fixed

- Import resolution fix

## [1.0.1] - 2025-04-17

### Added

- Initial release
<!-- END AUTO-GENERATED FROM ROOT CHANGELOG.md -->
