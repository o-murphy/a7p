#!/usr/bin/env python3
"""Codegen CLI for schema/a7p.schema.json.

Generates a pre-compiled, per-language validator from the canonical schema
so it doesn't have to be built at import time. See docs/DESIGN-schema-unification.md
for why (the JSON Schema + Quicktype/codegen plan) and README.md at the repo
root for usage and the numbers behind it.

Usage:
    python scripts/compile.py --python
    python scripts/compile.py --ts      (not yet implemented)
    python scripts/compile.py --dart    (not yet implemented)
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "a7p.schema.json"


def compile_python() -> None:
    import fastjsonschema

    out_path = REPO_ROOT / "py" / "src" / "a7p" / "_compiled_schema.py"
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
    import json

    schema = json.loads(schema_text)
    code = fastjsonschema.compile_to_code(schema)

    match = re.search(r"^def (validate_\S+)\(", code, re.MULTILINE)
    if not match:
        sys.exit("could not find the generated entrypoint function name")
    entrypoint = match.group(1)

    header = (
        "# GENERATED FILE -- DO NOT EDIT BY HAND.\n"
        "# Source:      schema/a7p.schema.json\n"
        "# Regenerate:  python scripts/compile.py --python\n"
        f"# fastjsonschema version used to generate this file: {fastjsonschema.VERSION}\n\n"
    )
    # fastjsonschema names the entrypoint after the schema's $id, which is an
    # implementation detail of this generator, not something callers should
    # depend on -- alias it to a stable name.
    footer = f"\n\nvalidate = {entrypoint}\n"

    out_path.write_text(header + code + footer, encoding="utf-8")
    print(f"wrote {out_path} ({len(code)} bytes, entrypoint {entrypoint})")


def compile_ts() -> None:
    sys.exit(
        "not implemented yet: js still validates with yup, not ajv. "
        "Migrate js/src/validate.ts to ajv first (see docs/DESIGN-schema-unification.md), "
        "then this can call `ajv compile --standalone` the same way --python calls fastjsonschema."
    )


def compile_dart() -> None:
    sys.exit(
        "not implemented yet: dart validates with a hand-written A7pValidator, "
        "not a schema-driven library. No standalone-codegen JSON Schema validator "
        "for Dart has been evaluated yet."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--python", action="store_true", help="regenerate py/'s compiled validator")
    group.add_argument("--ts", action="store_true", help="(not yet implemented)")
    group.add_argument("--dart", action="store_true", help="(not yet implemented)")
    args = parser.parse_args()

    if args.python:
        compile_python()
    elif args.ts:
        compile_ts()
    elif args.dart:
        compile_dart()


if __name__ == "__main__":
    main()
