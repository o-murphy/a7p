/// Display-unit constraints for `.a7p` fields, ported 1:1 from the
/// original ArcherBC2 app's field specs (`profile.clj`, `double-in-range?`
/// / `int-in-range?` / `string-shorter-than?`).
///
/// These are the ranges shown to the user while editing (e.g. "0.00–100.00
/// in/turn" for twist) — distinct from [A7pValidator], which checks the
/// raw on-wire integers actually stored in the protobuf. The scale factor
/// between the two is always `10^fractionDigits`
/// (e.g. r_twist raw 0–10000 ⇔ display 0.00–100.00, fractionDigits: 2).
library;

class A7pFieldRange {
  const A7pFieldRange({
    required this.min,
    required this.max,
    required this.fractionDigits,
    this.unit,
    int? uiFractionDigits,
  }) : _uiFractionDigits = uiFractionDigits;

  final double min;
  final double max;

  /// Scale factor (`10^fractionDigits`) between the display-unit value and
  /// the raw on-wire integer range in [A7pValidator] — ported 1:1 from the
  /// original app's `double-in-range?` spec. Changing this changes what
  /// gets written to the `.a7p` file, so it must match the original app's
  /// spec exactly regardless of UI preferences.
  final int fractionDigits;

  /// Decimal places actually shown/accepted while editing, when that's
  /// coarser than the wire scale allows (e.g. showing whole meters for a
  /// field whose raw value is scaled ×100). Defaults to [fractionDigits]
  /// when not overridden. Never wider than [fractionDigits] — the raw
  /// scale is always the ceiling on precision.
  int get uiFractionDigits => _uiFractionDigits ?? fractionDigits;
  final int? _uiFractionDigits;

  /// Unit label for display (e.g. "in/turn", "m/s"). Null where the
  /// original app shows no unit (indices, dimensionless coefficients).
  final String? unit;

  /// Rounds [value] to a raw on-wire integer using this field's scale.
  int toRaw(double value) => (value * _scale).round();

  /// Converts a raw on-wire integer back to a display-unit double.
  double fromRaw(int raw) => raw / _scale;

  double get _scale => _pow10(fractionDigits);

  static double _pow10(int n) {
    var r = 1.0;
    for (var i = 0; i < n; i++) {
      r *= 10;
    }
    return r;
  }
}

class A7pStringRange {
  const A7pStringRange({required this.maxLength, this.required = true});

  final int maxLength;
  final bool required;
}

abstract final class A7pFieldConstraints {
  // ── Strings ──────────────────────────────────────────────────────────────
  static const profileName = A7pStringRange(maxLength: 50);
  static const cartridgeName = A7pStringRange(maxLength: 50);
  static const bulletName = A7pStringRange(maxLength: 50);
  static const caliber = A7pStringRange(maxLength: 50);
  static const shortNameTop = A7pStringRange(maxLength: 8);
  static const shortNameBot = A7pStringRange(maxLength: 8);
  static const deviceUuid = A7pStringRange(maxLength: 50, required: false);
  static const userNote = A7pStringRange(maxLength: 1024, required: false);

  // ── Rifle ────────────────────────────────────────────────────────────────
  static const sightHeight = A7pFieldRange(
    min: -5000,
    max: 5000,
    fractionDigits: 0,
    unit: 'mm',
  );
  static const twist = A7pFieldRange(
    min: 0.0,
    max: 100.0,
    fractionDigits: 2,
    unit: 'in/turn',
  );

  // ── Zeroing ──────────────────────────────────────────────────────────────
  static const zeroX = A7pFieldRange(
    min: -200.0,
    max: 200.0,
    fractionDigits: 3,
    unit: 'click',
  );
  static const zeroY = A7pFieldRange(
    min: -200.0,
    max: 200.0,
    fractionDigits: 3,
    unit: 'click',
  );

  // ── Cartridge / powder ──────────────────────────────────────────────────
  static const muzzleVelocity = A7pFieldRange(
    min: 10.0,
    max: 3000.0,
    fractionDigits: 1,
    uiFractionDigits: 0,
    unit: 'm/s',
  );
  static const zeroTemperature = A7pFieldRange(
    min: -100,
    max: 100,
    fractionDigits: 0,
    unit: '°C',
  );
  static const powderTempSensitivity = A7pFieldRange(
    min: 0.0,
    max: 5.0,
    fractionDigits: 3,
    unit: '%/15°C',
  );

  // ── Zeroing atmosphere ───────────────────────────────────────────────────
  static const zeroAirTemperature = A7pFieldRange(
    min: -100,
    max: 100,
    fractionDigits: 0,
    unit: '°C',
  );
  static const zeroAirPressure = A7pFieldRange(
    min: 300.0,
    max: 1500.0,
    fractionDigits: 1,
    uiFractionDigits: 0,
    unit: 'hPa',
  );
  static const zeroAirHumidity = A7pFieldRange(
    min: 0,
    max: 100,
    fractionDigits: 0,
    unit: '%',
  );
  static const zeroWindPitch = A7pFieldRange(
    min: -90,
    max: 90,
    fractionDigits: 0,
    unit: '°',
  );
  static const zeroPowderTemperature = A7pFieldRange(
    min: -100,
    max: 100,
    fractionDigits: 0,
    unit: '°C',
  );

  // ── Bullet ───────────────────────────────────────────────────────────────
  static const bulletDiameter = A7pFieldRange(
    min: 0.001,
    max: 50.0,
    fractionDigits: 3,
    unit: 'in',
  );
  static const bulletWeight = A7pFieldRange(
    min: 1.0,
    max: 6553.5,
    fractionDigits: 1,
    unit: 'gr',
  );
  static const bulletLength = A7pFieldRange(
    min: 0.01,
    max: 200.0,
    fractionDigits: 3,
    unit: 'in',
  );

  // ── Drag model / ballistic coefficient ──────────────────────────────────
  static const bc = A7pFieldRange(
    min: 0.0,
    max: 10.0,
    fractionDigits: 4,
    uiFractionDigits: 3,
  );
  static const coefMv = A7pFieldRange(
    min: 0.0,
    max: 3000.0,
    fractionDigits: 1,
    uiFractionDigits: 0,
    unit: 'm/s',
  );
  static const customDragCd = A7pFieldRange(
    min: 0.0,
    max: 10.0,
    fractionDigits: 4,
  );
  static const customDragMach = A7pFieldRange(
    min: 0.0,
    max: 10.0,
    fractionDigits: 4,
    uiFractionDigits: 2,
    unit: 'Ma',
  );

  // ── Distances ────────────────────────────────────────────────────────────
  static const distance = A7pFieldRange(
    min: 1.0,
    max: 3000.0,
    fractionDigits: 2,
    uiFractionDigits: 0,
    unit: 'm',
  );
  static const distancesCountMin = 1;
  static const distancesCountMax = 200;

  // ── Switches (sight positions) ──────────────────────────────────────────
  static const reticleIdx = A7pFieldRange(min: 0, max: 255, fractionDigits: 0);

  /// `profile.clj`'s 0–4 is a bug in the original app; the device actually
  /// accepts 0–6 (0 = unset/default, seen on real shipped profiles for
  /// switches with `distanceFrom == INDEX`; 1–6 are real zoom levels),
  /// matching `A7pValidator`.
  static const zoom = A7pFieldRange(min: 0, max: 6, fractionDigits: 0);
  static const switchesCountMin = 4;

  // ── Ballistic coefficient table sizes ───────────────────────────────────
  static const coefRowsMaxG1G7 = 5;
  static const coefRowsMaxCustom = 200;
}
