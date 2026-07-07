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
## [1.2.0-alpha.1] - 2026-07-08

### Changed

- Validation now runs against the shared `schema/a7p.schema.json` via
  `schema_validator.py` (`fastjsonschema`-compiled, `jsonschema` fallback
  for full error lists) instead of the hand-written `yupy_schema.py`
  (kept temporarily, unused by the public API, as a reference/safety net)
- `proto/profedit.proto` now lives once at the repo root instead of a
  local copy under `proto/`
<!-- END AUTO-GENERATED FROM ROOT CHANGELOG.md -->
