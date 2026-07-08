#!/usr/bin/env bash
# Regenerates the per-language protobuf bindings from proto/profedit.proto
# (the canonical copy, shared by py/js/dart/go -- see
# docs/DESIGN-schema-unification.md, "Наступні кроки" step 0).
#
# Usage:
#   scripts/generate_proto.sh            # all four languages
#   scripts/generate_proto.sh --python
#   scripts/generate_proto.sh --ts
#   scripts/generate_proto.sh --dart
#   scripts/generate_proto.sh --go
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

run_go() {
  echo "== go =="
  # protoc-gen-go's default (paths=import) mode recreates the *entire*
  # go_package path under --go_out (i.e. .../github.com/o-murphy/a7p/go/a7p/profedit/profedit.pb.go);
  # paths=source_relative instead mirrors proto/profedit.proto's own location
  # (just "profedit.proto", no subdirectory), neither of which lands
  # directly at go/a7p/profedit/ -- so generate into a scratch dir and
  # copy the one file we want out of the go_package-shaped tree.
  local scratch
  scratch="$(mktemp -d)"
  trap 'rm -rf "$scratch"' RETURN
  protoc \
    --go_out="$scratch" \
    -I "$REPO_ROOT/proto" \
    "$PROTO"
  mkdir -p "$REPO_ROOT/go/a7p/profedit"
  cp "$scratch/github.com/o-murphy/a7p/go/a7p/profedit/profedit.pb.go" \
     "$REPO_ROOT/go/a7p/profedit/profedit.pb.go"
  echo "wrote go/a7p/profedit/profedit.pb.go"
}

if [ "$#" -eq 0 ]; then
  run_python
  run_ts
  run_dart
  run_go
  exit 0
fi

for arg in "$@"; do
  case "$arg" in
    --python) run_python ;;
    --ts) run_ts ;;
    --dart) run_dart ;;
    --go) run_go ;;
    *)
      echo "unknown flag: $arg (expected --python, --ts, --dart, --go)" >&2
      exit 1
      ;;
  esac
done
