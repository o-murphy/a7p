# a7p

A7P ballistic profile format for Dart — encode/decode, MD5-hash-prefixed
wire format, field validation, and field constraints (raw wire scale vs.
UI display precision).

Extracted from `archerbc2_flutter/packages/a7p` so the format can be
shared as a normal pub dependency (path or git) instead of being vendored
separately into each consuming app.

## Format

A `.a7p` file is `[32-byte MD5 hex string][protobuf-encoded Payload bytes]`
— the hash is stored as ASCII hex text, not raw binary. See
`lib/src/a7p_file.dart`.

## Regenerating the protobuf bindings

Requires `protoc` (the Protocol Buffers compiler) and the Dart plugin —
once per machine:

```sh
# Linux
sudo apt-get install -y protobuf-compiler
# macOS
brew install protobuf

dart pub global activate protoc_plugin
```

Then, after editing `proto/profedit.proto`:

```sh
dart run bin/generate_proto.dart
```

## Testing

```sh
dart pub get
dart analyze
dart test
```

## Formatting

```sh
dart format lib test bin
```

## License

LGPL-3.0 — see [LICENSE](LICENSE).
