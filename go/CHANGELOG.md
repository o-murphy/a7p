# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Version numbers are derived directly from git tags: `go.mod` lives at the
repo root (module `github.com/o-murphy/a7p`), so the same `vX.Y.Z` tag that
versions `py`/`js`/`dart` versions this module too -- nothing is hand-bumped
in this file.

Entries below this point are generated from the repo root's `CHANGELOG.md`
by `scripts/ci/sync_changelogs.py` -- edit that file, not this one, then
regenerate. `go` had no separate `CHANGELOG.md` of its own before merging
into the `a7p` monorepo, so there's no frozen pre-merge history here
to preserve (unlike `js`/`dart`).

<!-- BEGIN AUTO-GENERATED FROM ROOT CHANGELOG.md -->
## [Unreleased]

## [1.2.1] - 2026-07-09

`go` merged from `o-murphy/a7p-go` into this monorepo, with full git
history preserved — see `docs/DESIGN-schema-unification.md` for the design
behind this merge.

### Changed

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

[Unreleased]: https://github.com/o-murphy/a7p/compare/v1.2.0...HEAD
[1.2.1]: https://github.com/o-murphy/a7p/compare/v1.2.0...v1.2.1
<!-- END AUTO-GENERATED FROM ROOT CHANGELOG.md -->
