import 'package:json_schema/json_schema.dart';

import 'generated/a7p_schema.g.dart';
import 'proto/profedit.pb.dart';

class A7pFieldError {
  final String field;
  final String message;
  const A7pFieldError(this.field, this.message);

  @override
  String toString() => '$field: $message';
}

class A7pValidationException implements Exception {
  final List<A7pFieldError> errors;
  const A7pValidationException(this.errors);

  @override
  String toString() => 'A7P validation failed:\n${errors.join('\n')}';
}

class A7pValidator {
  // Built once from the embedded schema constant (kA7pSchemaJson, generated
  // by scripts/compile.py --dart) and reused for every validate() call --
  // JsonSchema.create() parses the whole schema, so this avoids repeating
  // that work per validation the way a fresh JsonSchema.create() call per
  // validate() would.
  static JsonSchema? _schemaCache;
  static JsonSchema get _schema =>
      _schemaCache ??= JsonSchema.create(kA7pSchemaJson);

  static void validate(Payload payload) {
    final errors = <A7pFieldError>[];
    if (!payload.hasProfile()) {
      errors.add(const A7pFieldError('payload', 'missing profile'));
      throw A7pValidationException(errors);
    }

    final data = _payloadToJson(payload);
    final results = _schema.validate(data);
    for (final e in results.errors) {
      errors.add(A7pFieldError(_fieldPath(e.instancePath), e.message));
    }

    // Not expressible in plain JSON Schema (see coef_rows.x-unique-except-zero
    // in schema/a7p.schema.json): all 'mv' values must be unique except that
    // any number of rows may have mv == 0. Checked separately, same as py's
    // schema_validator.py.
    final mvError = _uniqueMvError(payload.profile.coefRows);
    if (mvError != null) errors.add(mvError);

    if (errors.isNotEmpty) throw A7pValidationException(errors);
  }

  static A7pFieldError? _uniqueMvError(List<CoefRow> rows) {
    final seen = <int>{};
    for (final r in rows) {
      if (r.mv != 0 && !seen.add(r.mv)) {
        return const A7pFieldError(
          'coef_rows',
          "'mv' values must be unique, except for mv == 0",
        );
      }
    }
    return null;
  }

  // json_schema reports errors as JSON Pointers rooted at the whole Payload
  // (e.g. "/profile/switches/0/c_idx"); strip the "/profile" prefix so field
  // paths read the same as before this migration ("switches/0/c_idx").
  static String _fieldPath(String instancePath) {
    var path = instancePath;
    if (path.startsWith('/profile')) {
      path = path.substring('/profile'.length);
    }
    if (path.startsWith('/')) path = path.substring(1);
    return path.isEmpty ? 'payload' : path;
  }

  // Converts the protobuf Payload into the plain snake_case JSON shape
  // schema/a7p.schema.json is written against -- the same shape
  // MessageToDict(preserving_proto_field_name=True) produces in py. Dart
  // protobuf's own writeToJsonMap() uses camelCase (proto3 JSON mapping),
  // which wouldn't match the schema's property names, so this is built by
  // hand instead.
  static Map<String, dynamic> _payloadToJson(Payload payload) {
    final p = payload.profile;
    return {
      'profile': {
        'profile_name': p.profileName,
        'cartridge_name': p.cartridgeName,
        'bullet_name': p.bulletName,
        'short_name_top': p.shortNameTop,
        'short_name_bot': p.shortNameBot,
        'caliber': p.caliber,
        'device_uuid': p.deviceUuid,
        'user_note': p.userNote,
        'zero_x': p.zeroX,
        'zero_y': p.zeroY,
        'sc_height': p.scHeight,
        'r_twist': p.rTwist,
        'twist_dir': p.twistDir.name,
        'c_muzzle_velocity': p.cMuzzleVelocity,
        'c_zero_temperature': p.cZeroTemperature,
        'c_t_coeff': p.cTCoeff,
        'c_zero_distance_idx': p.cZeroDistanceIdx,
        'c_zero_air_temperature': p.cZeroAirTemperature,
        'c_zero_air_pressure': p.cZeroAirPressure,
        'c_zero_air_humidity': p.cZeroAirHumidity,
        'c_zero_w_pitch': p.cZeroWPitch,
        'c_zero_p_temperature': p.cZeroPTemperature,
        'b_diameter': p.bDiameter,
        'b_weight': p.bWeight,
        'b_length': p.bLength,
        'bc_type': p.bcType.name,
        'switches': p.switches.map(_switchToJson).toList(),
        'distances': p.distances.toList(),
        'coef_rows': p.coefRows.map(_coefRowToJson).toList(),
      },
    };
  }

  static Map<String, dynamic> _switchToJson(SwPos sw) => {
    'c_idx': sw.cIdx,
    'distance_from': sw.distanceFrom.name,
    'distance': sw.distance,
    'reticle_idx': sw.reticleIdx,
    'zoom': sw.zoom,
  };

  static Map<String, dynamic> _coefRowToJson(CoefRow r) => {
    'bc_cd': r.bcCd,
    'mv': r.mv,
  };
}
