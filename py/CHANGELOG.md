# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Version numbers are derived from git tags via `setuptools_scm`, not hand-bumped
in this file.

Entries below this point are generated from the repo root's `CHANGELOG.md`
by `scripts/ci/sync_changelogs.py` — edit that file, not this one, then
regenerate. `py` had no separate `CHANGELOG.md` of its own before merging
into the `a7p` monorepo, so there's no frozen pre-merge history here
to preserve (unlike `js`/`dart`).

<!-- BEGIN AUTO-GENERATED FROM ROOT CHANGELOG.md -->
## [Unreleased]

## [1.2.4] - 2026-07-16

### Removed

- `yupy` dependency and the hand-written `src/a7p/yupy_schema.py` validator it
  backed — unused by the public `a7p.validate()` path since the migration to
  `schema_validator.py` (`fastjsonschema`/`jsonschema` against
  `schema/a7p.schema.json`), and kept only as a reference/regression suite
  (`tests/test_yupy_schema.py`) until now
- `exceptions.YupyViolation` and `exceptions.A7PYupyValidationError` — folded
  into plain `Violation`/`A7PValidationError`; `A7PValidationError` no longer
  splits errors into `.violations`/`.yupy_violations`/`.all_violations`, just
  one `.violations` list

### Changed

- CLI flag `--disable-yupy` renamed to `--disable-validator`

## [1.2.3] - 2026-07-14

### Fixed

- `caliber`, `profile_name`, `cartridge_name`, `bullet_name`,
  `short_name_top`, and `short_name_bot` now accept an empty string,
  matching real device profiles — `_compiled_schema.py` and the bundled
  `a7p.schema.json` regenerated from `schema/a7p.schema.json`

## [1.2.2] - 2026-07-09

### Changed
- Updated dependencies

## [1.2.1] - 2026-07-09

### No changes since 1.2.0 (patch has been applied to js package)

## [1.2.0] - 2026-07-08

### Changed

- Validation now runs against the shared `schema/a7p.schema.json` via
  `schema_validator.py` (`fastjsonschema`-compiled, `jsonschema` fallback
  for full error lists) instead of the hand-written `yupy_schema.py`
  (kept temporarily, unused by the public API, as a reference/safety net)
- `proto/profedit.proto` now lives once at the repo root instead of a
  local copy under `proto/`

[Unreleased]: https://github.com/o-murphy/a7p/compare/v1.2.4...HEAD
[1.2.4]: https://github.com/o-murphy/a7p/compare/v1.2.3...v1.2.4
[1.2.3]: https://github.com/o-murphy/a7p/compare/v1.2.2...v1.2.3
[1.2.2]: https://github.com/o-murphy/a7p/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/o-murphy/a7p/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/o-murphy/a7p/releases/tag/v1.2.0
<!-- END AUTO-GENERATED FROM ROOT CHANGELOG.md -->
