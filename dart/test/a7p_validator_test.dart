import 'package:a7p/a7p.dart';
import 'package:test/test.dart';

// Mirrors schema/fixtures/valid/g1_profile.json (trimmed: 4 distances
// instead of 200, matching schema's switches minItems 4), kept as one
// shared base so each invalid-case test only has to describe its mutation.
Payload _validPayload() {
  return Payload(
    profile: Profile(
      profileName: '338LM BARNES 300GR OTM',
      cartridgeName: 'BARNES 300GR OTM',
      bulletName: 'BARNES 300GR OTM',
      shortNameTop: '.338LM',
      shortNameBot: '300gr',
      caliber: '.338 Lapua Magnum',
      deviceUuid: '',
      userNote: '\n',
      zeroX: 0,
      zeroY: 0,
      scHeight: 90,
      rTwist: 1000,
      twistDir: TwistDir.RIGHT,
      cMuzzleVelocity: 7920,
      cZeroTemperature: 15,
      cTCoeff: 1000,
      cZeroDistanceIdx: 0,
      cZeroAirTemperature: 15,
      cZeroAirPressure: 10000,
      cZeroAirHumidity: 50,
      cZeroWPitch: 0,
      cZeroPTemperature: 15,
      bDiameter: 338,
      bWeight: 3000,
      bLength: 1800,
      bcType: GType.G1,
      switches: [
        SwPos(
          cIdx: 255,
          distanceFrom: DType.VALUE,
          distance: 10000,
          reticleIdx: 0,
          zoom: 1,
        ),
        SwPos(
          cIdx: 255,
          distanceFrom: DType.VALUE,
          distance: 20000,
          reticleIdx: 0,
          zoom: 2,
        ),
        SwPos(
          cIdx: 255,
          distanceFrom: DType.VALUE,
          distance: 30000,
          reticleIdx: 0,
          zoom: 3,
        ),
        SwPos(
          cIdx: 255,
          distanceFrom: DType.VALUE,
          distance: 100000,
          reticleIdx: 0,
          zoom: 4,
        ),
      ],
      distances: [10000, 20000, 25000, 30000],
      coefRows: [CoefRow(bcCd: 7160, mv: 7920)],
    ),
  );
}

void main() {
  test('a real g1 profile passes validation', () {
    expect(() => A7pValidator.validate(_validPayload()), returnsNormally);
  });

  for (final field in [
    'profileName',
    'cartridgeName',
    'bulletName',
    'shortNameTop',
    'shortNameBot',
    'caliber',
  ]) {
    test(
      'required string field $field may be empty (mirrors schema/fixtures/valid/empty_required_strings.json)',
      () {
        final payload = _validPayload();
        switch (field) {
          case 'profileName':
            payload.profile.profileName = '';
          case 'cartridgeName':
            payload.profile.cartridgeName = '';
          case 'bulletName':
            payload.profile.bulletName = '';
          case 'shortNameTop':
            payload.profile.shortNameTop = '';
          case 'shortNameBot':
            payload.profile.shortNameBot = '';
          case 'caliber':
            payload.profile.caliber = '';
        }
        expect(() => A7pValidator.validate(payload), returnsNormally);
      },
    );
  }

  test('a real custom-drag profile passes validation', () {
    final payload = _validPayload();
    payload.profile
      ..bcType = GType.CUSTOM
      ..coefRows.clear()
      ..coefRows.addAll([
        CoefRow(bcCd: 1000, mv: 8000),
        CoefRow(bcCd: 1100, mv: 9000),
      ]);
    expect(() => A7pValidator.validate(payload), returnsNormally);
  });

  test('missing profile is rejected', () {
    expect(
      () => A7pValidator.validate(Payload()),
      throwsA(
        isA<A7pValidationException>().having(
          (e) => e.errors.single.field,
          'field',
          'payload',
        ),
      ),
    );
  });

  test(
    'value out of range is rejected (mirrors schema/fixtures/invalid/value_out_of_range.json)',
    () {
      final payload = _validPayload();
      payload.profile.cMuzzleVelocity = 99; // schema minimum is 100
      expect(
        () => A7pValidator.validate(payload),
        throwsA(
          isA<A7pValidationException>().having(
            (e) => e.errors.single.field,
            'field',
            'c_muzzle_velocity',
          ),
        ),
      );
    },
  );

  test(
    'string too long is rejected (mirrors schema/fixtures/invalid/string_too_long.json)',
    () {
      final payload = _validPayload();
      payload.profile.profileName = 'x' * 51; // schema maxLength is 50
      expect(
        () => A7pValidator.validate(payload),
        throwsA(
          isA<A7pValidationException>().having(
            (e) => e.errors.single.field,
            'field',
            'profile_name',
          ),
        ),
      );
    },
  );

  test(
    'too few switches is rejected (mirrors schema/fixtures/invalid/too_few_switches.json)',
    () {
      final payload = _validPayload();
      payload.profile.switches.removeLast(); // schema minItems is 4
      expect(
        () => A7pValidator.validate(payload),
        throwsA(
          isA<A7pValidationException>().having(
            (e) => e.errors.single.field,
            'field',
            'switches',
          ),
        ),
      );
    },
  );

  test('c_idx in the undefined 201-254 gap is rejected', () {
    final payload = _validPayload();
    payload.profile.switches[0].cIdx = 210;
    expect(
      () => A7pValidator.validate(payload),
      throwsA(isA<A7pValidationException>()),
    );
  });

  test(
    'duplicate non-zero mv is rejected (mirrors schema/fixtures/invalid/duplicate_mv.json)',
    () {
      final payload = _validPayload();
      payload.profile
        ..bcType = GType.CUSTOM
        ..coefRows.clear()
        ..coefRows.addAll([
          CoefRow(bcCd: 1000, mv: 8000),
          CoefRow(bcCd: 1100, mv: 8000),
        ]);
      expect(
        () => A7pValidator.validate(payload),
        throwsA(
          isA<A7pValidationException>().having(
            (e) => e.errors.single.field,
            'field',
            'coef_rows',
          ),
        ),
      );
    },
  );

  test('mv == 0 may repeat across rows', () {
    final payload = _validPayload();
    payload.profile
      ..bcType = GType.CUSTOM
      ..coefRows.clear()
      ..coefRows.addAll([
        CoefRow(bcCd: 1000, mv: 0),
        CoefRow(bcCd: 1100, mv: 0),
      ]);
    expect(() => A7pValidator.validate(payload), returnsNormally);
  });
}
