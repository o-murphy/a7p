# a7p-cross

Cross-language tooling for the `.a7p` ballistic profile format (`py` (the
`a7p` Python package), `js`, `dart`).

## proto/profedit.proto

Canonical `.proto` source for the wire *shape* of a profile (as opposed to
`schema/a7p.schema.json`, which covers value ranges/constraints — see
`docs/DESIGN-schema-unification.md`). Previously copied verbatim into
`py/proto/`, `js/src/proto/`, and `dart/proto/`; now lives here once, since
it's only needed at codegen build-time (not packaged into any of the three
language distributions) and each of `py`/`js`/`dart` is checked out inside
this tree as a submodule.

Regenerate all three languages' bindings after editing the `.proto`:

```sh
scripts/generate_proto.sh            # all three
scripts/generate_proto.sh --python   # or one at a time
scripts/generate_proto.sh --ts
scripts/generate_proto.sh --dart
```

This shells out to each language's own toolchain (`protoc` directly for
`python`; `yarn build:proto` for `ts`, which wraps `ts_proto`; `dart run
bin/generate_proto.dart` for `dart`, which additionally resolves the
`protoc-gen-dart` plugin path portably across platforms) — it's a thin
orchestrator, not a reimplementation, so each language keeps whatever
plugin-specific logic it already had.

## schema/a7p.schema.json

Canonical JSON Schema for the `.a7p` profile format — the single source of
truth for field ranges, string lengths, enum values, and the coef_rows/bcType
conditional rules that used to be hand-duplicated across `py`, `js`,
and `dart`. See `docs/DESIGN-schema-unification.md` for the full design
and the list of discrepancies found (and fixed) between the three repos'
old hand-written validators.

## Regenerating per-language validators

`compile.py` turns the schema into a pre-compiled validator for a target
language, so the compile step happens once at build time instead of on
every process start.

```sh
python scripts/compile.py --python   # implemented
python scripts/compile.py --ts       # not yet -- js still uses yup, not ajv
python scripts/compile.py --dart     # implemented
```

### `--python`

Runs `fastjsonschema.compile_to_code()` on `a7p.schema.json` and writes the
result to `py/src/a7p/_compiled_schema.py` (a generated file — do not
edit it by hand, and do not skip regenerating it after changing the schema).

`a7p/schema_validator.py` imports this generated module for the common
(valid-payload) case. Building the validator function from the schema with
`fastjsonschema.compile()` at import time costs ~20ms; importing a
pre-generated module instead costs closer to ~2-5ms, so this is worth doing
even though it adds a step to remember. It only matters if `a7p` is invoked
as a fresh process per file (a pre-commit hook, a serverless function, one
CLI invocation per file in CI); if you always call it as a library inside a
longer-lived process, or run the CLI over a whole directory in one process,
the ~20ms is a one-time cost already invisible next to everything else that
process does.

**Run this whenever `a7p.schema.json` changes** and commit the regenerated
`_compiled_schema.py` alongside it — the two must never drift, which is
exactly the failure mode this whole schema-unification effort exists to
eliminate. There's no CI check enforcing this yet; until there is, treat it
as a manual step of editing the schema.

### `--dart`

There's no Dart equivalent of `fastjsonschema.compile_to_code()` — no
standalone-codegen JSON Schema validator for Dart exists. Instead, this step
embeds `a7p.schema.json` as a raw Dart string constant in
`dart/lib/src/generated/a7p_schema.g.dart` (a generated file — do not edit it
by hand), and `A7pValidator` (in `dart/lib/src/a7p_validator.dart`) builds a
`JsonSchema` from it once (a lazy singleton) and reuses it for every
`validate()` call via the `json_schema` package.

The embedding has to survive Flutter AOT/web builds without asset bundling
(Flutter-only, wouldn't work in plain Dart VM/CLI use) or `package:` URI
resolution (unreliable in AOT/release builds) — a plain Dart string constant
compiles like any other code, so it works the same everywhere. It's a raw
string (`r"""..."""`) because the schema uses `$ref`/`$defs`/`$id`, and Dart
would otherwise try to interpolate the `$`.

**Run this whenever `a7p.schema.json` changes** and commit the regenerated
`a7p_schema.g.dart` alongside it, same as `--python`.

On failure, `schema_validator.py` falls back to `jsonschema` (pure Python,
slower, but reports every violation instead of only the first one) so the
existing "list every invalid field, not just the first" behavior is
preserved — that fallback path is unaffected by this compile step, since
`jsonschema.Draft202012Validator` is built directly from the schema JSON at
the point it's actually needed, not pre-compiled.

## Benchmarked on the real gallery corpus

484 real `.a7p` files (`py/a7p-lib/gallery/` + test fixtures), compared
against the existing hand-written `yupy` validator in `py`:

| Validator                             | us/file | vs `yupy`           |
| ------------------------------------- | ------- | ------------------- |
| `yupy` (old, hand-written)            | 623     | 1x                  |
| `jsonschema` (pure Python)            | 2702    | 0.23x (4.3x slower) |
| `fastjsonschema` (compiled at import) | 116     | 5.4x faster         |

All three agree on the exact same 52/484 invalid files (all duplicate `mv`
values in `coef_rows`, the one rule not expressible in plain JSON Schema —
see `x-unique-except-zero` in the schema).

## schema/fixtures/

A small set of plain-JSON payloads (the same shape `MessageToDict` /
`protobuf.util.toJson` / `jsonEncode` on a `Payload` produce — snake_case
keys, no protobuf decoding needed) for language repos that don't have their
own corpus of real `.a7p` files to test against (`js` currently has no
test suite at all; `dart` has no real-file corpus of its own):

- `valid/g1_profile.json`, `valid/custom_profile.json` — real profiles
  pulled from `py/a7p-lib/gallery/`, one per `bc_type` branch of the
  `coef_rows` if/then (G1 vs CUSTOM have different `mv` ranges and
  `maxItems`).
- `invalid/duplicate_mv.json` — a real file from `.unvalidated/`, invalid
  only because of the one rule plain JSON Schema can't express (unique
  `mv` except 0).
- `invalid/string_too_long.json`, `value_out_of_range.json`,
  `too_few_switches.json`, `bad_enum.json` — synthetic, single-field
  mutations of `g1_profile.json`, each isolating exactly one schema rule
  (`maxLength`, `minimum`, `minItems`, `enum`) so a failing test points at
  one specific cause.

Regenerate/extend this set with `a7p` (via `uv run --project py`) or
any JSON-Schema validator against `schema/a7p.schema.json` — there's no
script for it yet since the set has been small and hand-picked so far.
