#!/usr/bin/env bash
# Regenerates the per-language protobuf bindings from proto/profedit.proto
# (the canonical copy, shared by py/js/dart -- see
# docs/DESIGN-schema-unification.md, "Наступні кроки" step 0).
#
# Usage:
#   scripts/generate_proto.sh            # all three languages
#   scripts/generate_proto.sh --python
#   scripts/generate_proto.sh --ts
#   scripts/generate_proto.sh --dart
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROTO="$REPO_ROOT/proto/profedit.proto"

run_python() {
  echo "== python =="
  protoc \
    --python_out="$REPO_ROOT/py/src/a7p" \
    --pyi_out="$REPO_ROOT/py/src/a7p" \
    -I "$REPO_ROOT/proto" \
    "$PROTO"
  echo "wrote py/src/a7p/profedit_pb2.py(.pyi)"
}

run_ts() {
  echo "== ts =="
  (cd "$REPO_ROOT/js" && yarn build:proto)
}

run_dart() {
  echo "== dart =="
  (cd "$REPO_ROOT/dart" && dart run bin/generate_proto.dart)
}

if [ "$#" -eq 0 ]; then
  run_python
  run_ts
  run_dart
  exit 0
fi

for arg in "$@"; do
  case "$arg" in
    --python) run_python ;;
    --ts) run_ts ;;
    --dart) run_dart ;;
    *)
      echo "unknown flag: $arg (expected --python, --ts, --dart)" >&2
      exit 1
      ;;
  esac
done
