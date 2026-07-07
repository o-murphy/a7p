"""Validates a `profedit_pb2.Payload` against the canonical .a7p JSON Schema
(bundled as a7p.schema.json, copied from a7p-cross/schema/a7p.schema.json).

Uses a7p._compiled_schema for the common (valid) case: a fastjsonschema
validator function pre-compiled to plain Python source by
`schema/compile.py --python` (see that script and README.md next to it),
rather than built with fastjsonschema.compile() at import time -- the
compile step itself costs ~20ms, which would otherwise be paid on every
`import a7p`. Regenerate it whenever schema/a7p.schema.json changes.

fastjsonschema stops at the first violation by design, so on failure the
same data is re-checked with jsonschema (pure Python, slower, but collects
every violation) to preserve the existing behavior of reporting all
violations at once when fail_fast=False. The one rule not expressible in
JSON Schema itself -- 'mv' values in coef_rows must be unique except for
mv == 0 -- is checked separately, as documented in the schema's
coef_rows.x-unique-except-zero.

`jsonschema` (the fallback) and the raw schema JSON it needs are both
loaded lazily, on first actual validation failure, rather than at module
load: importing jsonschema costs ~65ms on its own, which would otherwise
be paid by every `import a7p` even though the large majority of payloads
are valid and never touch that path.
"""

from google.protobuf.json_format import MessageToDict

from a7p import profedit_pb2
from a7p._compiled_schema import validate as _validate_fast
from fastjsonschema import JsonSchemaException as _FastJsonSchemaException

__all__ = ("validate", "SchemaValidationError")


class SchemaValidationError(Exception):
    """errors: list of (json_pointer_path, message) tuples."""

    def __init__(self, errors: list[tuple[str, str]]):
        self.errors = errors
        super().__init__("; ".join(f"{path}: {message}" for path, message in errors))


_slow_validator = None


def _get_slow_validator():
    global _slow_validator
    if _slow_validator is None:
        import json
        from importlib import resources

        import jsonschema

        with resources.files("a7p").joinpath("a7p.schema.json").open(
            "r", encoding="utf-8"
        ) as f:
            schema = json.load(f)
        _slow_validator = jsonschema.Draft202012Validator(schema)
    return _slow_validator


def _unique_mv_error(data: dict) -> tuple[str, str] | None:
    rows = data["profile"]["coef_rows"]
    mv_values = [row["mv"] for row in rows if row["mv"] != 0]
    if len(mv_values) != len(set(mv_values)):
        return "~/profile/coef_rows", "'mv' values must be unique, except for mv == 0"
    return None


def validate(payload: profedit_pb2.Payload, fail_fast: bool = False) -> None:
    """
    Raises:
        SchemaValidationError: If there are any violations.
    """
    data = MessageToDict(
        payload,
        always_print_fields_with_no_presence=True,
        preserving_proto_field_name=True,
    )

    schema_ok = True
    try:
        _validate_fast(data)
    except _FastJsonSchemaException:
        schema_ok = False

    if not schema_ok:
        slow_validator = _get_slow_validator()
        if fail_fast:
            first = next(slow_validator.iter_errors(data))
            path = "~/" + "/".join(str(p) for p in first.absolute_path)
            raise SchemaValidationError([(path, first.message)])
        errors = [
            ("~/" + "/".join(str(p) for p in e.absolute_path), e.message)
            for e in slow_validator.iter_errors(data)
        ]
        mv_error = _unique_mv_error(data)
        if mv_error:
            errors.append(mv_error)
        raise SchemaValidationError(errors)

    mv_error = _unique_mv_error(data)
    if mv_error:
        raise SchemaValidationError([mv_error])
