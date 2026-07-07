#!/usr/bin/env python3
"""Codegen CLI for schema/a7p.schema.json.

Generates a pre-compiled, per-language validator from the canonical schema
so it doesn't have to be built at import time. See docs/DESIGN-schema-unification.md
for why (the JSON Schema + Quicktype/codegen plan) and README.md at the repo
root for usage and the numbers behind it.

Usage:
    python scripts/compile.py --python
    python scripts/compile.py --ts
    python scripts/compile.py --dart
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
    """Compiles a7p.schema.json into a standalone ajv validator for js/.

    There's no `ajv compile --standalone` CLI flag -- ajv-cli's --spec= only
    covers draft7/draft2019-09, not the draft 2020-12 this schema uses.
    Standalone codegen only exists via ajv's JS API (Ajv2020 + standaloneCode()),
    so unlike --python this can't be done from Python directly; it shells out
    to js/scripts/build_schema_validator.mjs, the actual codegen script (kept
    in js/ so it can `require`/`import` the ajv devDependency already
    installed there). See that script for why the output is CommonJS (.cjs)
    rather than ESM despite js/ being "type": "module".
    """
    import subprocess

    script = REPO_ROOT / "js" / "scripts" / "build_schema_validator.mjs"
    result = subprocess.run(["node", str(script)], cwd=REPO_ROOT / "js")
    if result.returncode != 0:
        sys.exit(result.returncode)


def compile_dart() -> None:
    """Embeds a7p.schema.json as a raw Dart string constant.

    There's no Dart equivalent of fastjsonschema.compile_to_code() (no
    standalone-codegen JSON Schema validator for Dart) -- dart/ instead
    validates at runtime with the `json_schema` package against a JsonSchema
    built once from this embedded constant (a lazy singleton, see
    A7pValidator._schema in a7p_validator.dart). This step only has to solve
    getting the schema JSON to travel inside the compiled package (pub.dev
    install, Flutter AOT/web builds) without relying on asset bundling
    (Flutter-only) or package: URI resolution (unreliable in AOT/release
    builds) -- a plain Dart string constant works identically in VM, Flutter,
    and web.
    """
    import json

    out_path = REPO_ROOT / "dart" / "lib" / "src" / "generated" / "a7p_schema.g.dart"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    compact = json.dumps(schema)

    # $ref/$defs/$id are real JSON Schema keywords used throughout this file,
    # and Dart interpolates `$` in non-raw strings -- must stay a raw string.
    # Raw strings can't contain their own delimiter, so guard against it
    # (would need a different embedding strategy, e.g. base64, if it ever
    # trips -- see docs/DESIGN-schema-unification.md step 1 for why base64
    # wasn't the default choice).
    if '"""' in compact:
        sys.exit(
            'schema/a7p.schema.json now contains a literal `"""`, which '
            "breaks the r\"\"\"...\"\"\" raw-string embedding in generated "
            "a7p_schema.g.dart. Switch compile_dart() to a base64-encoded "
            "embedding instead."
        )

    header = (
        "// GENERATED FILE -- DO NOT EDIT BY HAND.\n"
        "// Source:      schema/a7p.schema.json\n"
        "// Regenerate:  python scripts/compile.py --dart\n\n"
    )
    body = f'const String kA7pSchemaJson = r"""\n{compact}\n""";\n'

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header + body, encoding="utf-8")
    print(f"wrote {out_path} ({len(compact)} bytes embedded)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--python", action="store_true", help="regenerate py/'s compiled validator")
    group.add_argument("--ts", action="store_true", help="regenerate js/'s standalone ajv validator")
    group.add_argument("--dart", action="store_true", help="regenerate dart/'s embedded schema constant")
    args = parser.parse_args()

    if args.python:
        compile_python()
    elif args.ts:
        compile_ts()
    elif args.dart:
        compile_dart()


if __name__ == "__main__":
    main()
