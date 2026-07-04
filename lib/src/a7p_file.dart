import 'dart:convert';
import 'dart:typed_data';

import 'package:crypto/crypto.dart';

import 'proto/profedit.pb.dart' as proto;

// .a7p binary format: [32 bytes MD5 hex string][protobuf bytes]
// The MD5 is stored as ASCII hex (e.g. "d41d8cd98f00b204e9800998ecf8427e"),
// NOT as 16 raw binary bytes — matching the Python a7p library.

class A7pParseException implements Exception {
  final String reason;
  const A7pParseException(this.reason);

  @override
  String toString() => 'A7P parse error: $reason';
}

abstract final class A7pFile {
  static Uint8List encode(proto.Payload payload) {
    final pb = payload.writeToBuffer();
    final hexHash = md5.convert(pb).toString(); // 32-char hex string
    return Uint8List.fromList([...ascii.encode(hexHash), ...pb]);
  }

  /// Throws [A7pParseException] on any error.
  static proto.Payload decode(Uint8List bytes) {
    if (bytes.length < 33) {
      throw const A7pParseException('file too small');
    }

    // Primary format: 32-byte ASCII-hex MD5 header + protobuf.
    final storedHex = ascii.decode(bytes.sublist(0, 32), allowInvalid: true);
    final pbAfterHex = bytes.sublist(32);
    if (storedHex == md5.convert(pbAfterHex).toString()) {
      try {
        final payload = proto.Payload.fromBuffer(pbAfterHex);
        if (payload.hasProfile()) return payload;
      } catch (e) {
        throw A7pParseException('protobuf decode failed: $e');
      }
    }

    // Fallback: 16 raw MD5 bytes (not ASCII hex) + protobuf — seen from
    // other .a7p writers in the wild even though the reference Python
    // library and the original desktop app only ever produce the 32-byte
    // hex form above.
    if (bytes.length >= 17) {
      final storedRaw = bytes.sublist(0, 16);
      final pbAfterRaw = bytes.sublist(16);
      if (_bytesEqual(storedRaw, md5.convert(pbAfterRaw).bytes)) {
        try {
          final payload = proto.Payload.fromBuffer(pbAfterRaw);
          if (payload.hasProfile()) return payload;
        } catch (e) {
          throw A7pParseException('protobuf decode failed: $e');
        }
      }
    }

    // Fallback: try whole file as raw protobuf (no header).
    try {
      final payload = proto.Payload.fromBuffer(bytes);
      if (payload.hasProfile()) return payload;
    } catch (_) {}

    throw const A7pParseException('not a valid .a7p file');
  }

  static bool _bytesEqual(List<int> a, List<int> b) {
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
}
