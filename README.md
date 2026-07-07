# a7p-cross

Cross-language tooling for the `.a7p` ballistic profile format (`py` (the
`a7p` Python package), `js`, `dart`).

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
python scripts/compile.py --dart     # not yet -- dart uses a hand-written A7pValidator
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
