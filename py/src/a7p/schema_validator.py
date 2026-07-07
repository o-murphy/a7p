"""Validates a `profedit_pb2.Payload` against the canonical .a7p JSON Schema
(bundled as a7p.schema.json, copied from a7p-cross/schema/a7p.schema.json).

Uses fastjsonschema for the common (valid) case, since it's ~5x faster than
the yupy validator it replaces. fastjsonschema stops at the first violation
by design, so on failure the same data is re-checked with jsonschema (pure
Python, slower, but collects every violation) to preserve the existing
behavior of reporting all violations at once when fail_fast=False. The one
rule not expressible in JSON Schema itself -- 'mv' values in coef_rows must
be unique except for mv == 0 -- is checked separately, as documented in the
schema's coef_rows.x-unique-except-zero.
"""

import json
from importlib import resources

import fastjsonschema
import jsonschema
from google.protobuf.json_format import MessageToDict

from a7p import profedit_pb2

__all__ = ("validate", "SchemaValidationError")


class SchemaValidationError(Exception):
    """errors: list of (json_pointer_path, message) tuples."""

    def __init__(self, errors: list[tuple[str, str]]):
        self.errors = errors
        super().__init__("; ".join(f"{path}: {message}" for path, message in errors))


with resources.files("a7p").joinpath("a7p.schema.json").open(
    "r", encoding="utf-8"
) as _f:
    _schema = json.load(_f)

_validate_fast = fastjsonschema.compile(_schema)
_slow_validator = jsonschema.Draft202012Validator(_schema)


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
    except fastjsonschema.JsonSchemaException:
        schema_ok = False

    if not schema_ok:
        if fail_fast:
            first = next(_slow_validator.iter_errors(data))
            path = "~/" + "/".join(str(p) for p in first.absolute_path)
            raise SchemaValidationError([(path, first.message)])
        errors = [
            ("~/" + "/".join(str(p) for p in e.absolute_path), e.message)
            for e in _slow_validator.iter_errors(data)
        ]
        mv_error = _unique_mv_error(data)
        if mv_error:
            errors.append(mv_error)
        raise SchemaValidationError(errors)

    mv_error = _unique_mv_error(data)
    if mv_error:
        raise SchemaValidationError([mv_error])
