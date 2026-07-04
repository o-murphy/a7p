import 'package:a7p/a7p.dart';
import 'package:test/test.dart';

void main() {
  group('uiFractionDigits does not change the on-wire raw scale', () {
    // Regression guard for lowering the UI's display/input precision on a
    // handful of fields (distance, pressure, velocity, BC, custom-model
    // Ma) — `toRaw`/`fromRaw` must keep using `fractionDigits` (ported 1:1
    // from the original app's `double-in-range?` spec), never
    // `uiFractionDigits`, or files written by this app would silently use
    // a different scale than the original app/real hardware expect.

    test('distance: raw scale stays ×100 (fractionDigits 2)', () {
      final c = A7pFieldConstraints.distance;
      expect(c.uiFractionDigits, 0);
      expect(c.toRaw(100), 10000);
      expect(c.fromRaw(10000), 100.0);
    });

    test('zeroAirPressure: raw scale stays ×10 (fractionDigits 1)', () {
      final c = A7pFieldConstraints.zeroAirPressure;
      expect(c.uiFractionDigits, 0);
      expect(c.toRaw(1000), 10000);
      expect(c.fromRaw(10000), 1000.0);
    });

    test('muzzleVelocity: raw scale stays ×10 (fractionDigits 1)', () {
      final c = A7pFieldConstraints.muzzleVelocity;
      expect(c.uiFractionDigits, 0);
      expect(c.toRaw(890), 8900);
      expect(c.fromRaw(8900), 890.0);
    });

    test('coefMv: raw scale stays ×10 (fractionDigits 1)', () {
      final c = A7pFieldConstraints.coefMv;
      expect(c.uiFractionDigits, 0);
      expect(c.toRaw(800), 8000);
    });

    test('bc: raw scale stays ×10000 (fractionDigits 4)', () {
      final c = A7pFieldConstraints.bc;
      expect(c.uiFractionDigits, 3);
      expect(c.toRaw(0.535), 5350);
      expect(c.fromRaw(5350), 0.535);
    });

    test('customDragMach: raw scale stays ×10000 (fractionDigits 4)', () {
      final c = A7pFieldConstraints.customDragMach;
      expect(c.uiFractionDigits, 2);
      expect(c.toRaw(1.25), 12500);
      expect(c.fromRaw(12500), 1.25);
    });

    test('fields without an override still use fractionDigits as-is', () {
      expect(
        A7pFieldConstraints.twist.uiFractionDigits,
        A7pFieldConstraints.twist.fractionDigits,
      );
      expect(
        A7pFieldConstraints.customDragCd.uiFractionDigits,
        A7pFieldConstraints.customDragCd.fractionDigits,
      );
    });
  });

  test('distances table caps at 200 rows, matching A7pValidator', () {
    expect(A7pFieldConstraints.distancesCountMax, 200);
    expect(A7pFieldConstraints.distancesCountMin, 1);
  });
}
