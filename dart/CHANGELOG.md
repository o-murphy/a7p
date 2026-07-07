# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Generated from the repo root's `CHANGELOG.md` (the single source of truth,
including this package's full history — see that file's own header) by
`scripts/ci/sync_changelogs.py` — edit that file, not this one, then
regenerate.

<!-- BEGIN AUTO-GENERATED FROM ROOT CHANGELOG.md -->
## [0.1.0] - 2026-07-05

First stable release, no changes from [0.1.0-beta.1](#010-beta1---2026-07-04).

## [0.1.0-beta.1] - 2026-07-04

### Added

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
<!-- END AUTO-GENERATED FROM ROOT CHANGELOG.md -->
