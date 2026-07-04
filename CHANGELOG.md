# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0-beta.1] - 2026-07-04

Initial extraction from `archerbc2_flutter/packages/a7p` into a standalone
package.

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

[Unreleased]: https://github.com/o-murphy/a7p-dart/compare/v0.1.0-beta.1...HEAD
[0.1.0-beta.1]: https://github.com/o-murphy/a7p-dart/releases/tag/v0.1.0-beta.1
