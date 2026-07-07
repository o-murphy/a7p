# a7p

A7P ballistic profile format for Dart — encode/decode, MD5-hash-prefixed
wire format, field validation, and field constraints (raw wire scale vs.
UI display precision).

[![License]](LICENSE)
[![Pub Version]][pub package]

![Linux] ![Windows] ![Android] ![iOS] ![macOS]

[![CI](https://github.com/o-murphy/a7p/actions/workflows/dart.yml/badge.svg)](https://github.com/o-murphy/a7p/actions/workflows/dart.yml)

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

Then, after editing `../proto/profedit.proto` (the canonical copy lives at
the `a7p` repo root, shared with the `py`/`js` packages — this only
works when `dart/` is checked out inside an `a7p` tree):

```sh
dart run bin/generate_proto.dart
```

## Regenerating the embedded validation schema

`A7pValidator` validates against `../schema/a7p.schema.json` (also shared
with `py`/`js`), embedded as a Dart string constant in
`lib/src/generated/a7p_schema.g.dart` — see that file's header and
`README.md` at the `a7p` repo root ("`--dart`" section) for why.
After editing the schema:

```sh
python scripts/compile.py --dart   # from the a7p repo root
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


<!-- REUSABLE LINKS -->

[License]: https://img.shields.io/badge/License-LGPL%20v3-blue.svg

[Pub Version]: https://img.shields.io/pub/v/a7p?logo=dart&cacheSeconds=0
[pub package]: https://pub.dev/packages/a7p

[Linux]: https://img.shields.io/badge/Linux-x86__64%20%7C%20arm64-grey?logo=linux&logoColor=black&labelColor=FCC624
[Windows]: https://img.shields.io/badge/x86__64-grey?logo=windows&logoColor=black&label=Windows&labelColor=0078D4
[Android]: https://img.shields.io/badge/Android-arm64%20%7C%20armv7%20%7C%20x86__64-grey?logo=android&logoColor=white&labelColor=3DDC84
[iOS]: https://img.shields.io/badge/iOS-arm64-grey?logo=apple&logoColor=white&labelColor=000000
[macOS]: https://img.shields.io/badge/macOS-arm64%20%7C%20x86__64-grey?logo=apple&logoColor=white&labelColor=000000
