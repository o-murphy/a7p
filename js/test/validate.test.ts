import { describe, expect, test } from '@jest/globals';
import { validate } from '../src/validate.js';
import { BcType, Payload, TwistDir } from '../src/types.js';
import { ValidationError } from '../src/errors.js';

// Mirrors schema/fixtures/valid/g1_profile.json (trimmed: 4 distances
// instead of 200, matching schema's switches minItems 4), kept as one
// shared base so each invalid-case test only has to describe its mutation.
function validPayload(): Payload {
    return {
        profile: {
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
            bcType: BcType.G1,
            switches: [
                { cIdx: 255, distanceFrom: 'VALUE', distance: 10000, reticleIdx: 0, zoom: 1 },
                { cIdx: 255, distanceFrom: 'VALUE', distance: 20000, reticleIdx: 0, zoom: 2 },
                { cIdx: 255, distanceFrom: 'VALUE', distance: 30000, reticleIdx: 0, zoom: 3 },
                { cIdx: 255, distanceFrom: 'VALUE', distance: 100000, reticleIdx: 0, zoom: 4 },
            ],
            distances: [10000, 20000, 25000, 30000],
            coefRows: [{ bcCd: 7160, mv: 7920 }],
        },
    };
}

describe('validate', () => {
    test('a real g1 profile passes validation', () => {
        expect(() => validate(validPayload())).not.toThrow();
    });

    test('a real custom-drag profile passes validation', () => {
        const payload = validPayload();
        payload.profile.bcType = BcType.CUSTOM;
        payload.profile.coefRows = [
            { bcCd: 1000, mv: 8000 },
            { bcCd: 1100, mv: 9000 },
        ];
        expect(() => validate(payload)).not.toThrow();
    });

    test('missing profile is rejected', () => {
        const payload = {} as Payload;
        expect(() => validate(payload)).toThrow(ValidationError);
        try {
            validate(payload);
        } catch (e) {
            expect((e as ValidationError).errors).toEqual(['payload: missing profile']);
        }
    });

    test('value out of range is rejected (mirrors schema/fixtures/invalid/value_out_of_range.json)', () => {
        const payload = validPayload();
        payload.profile.cMuzzleVelocity = 99; // schema minimum is 100
        expect(() => validate(payload)).toThrow(ValidationError);
        try {
            validate(payload);
        } catch (e) {
            expect((e as ValidationError).errors[0]).toMatch(/^c_muzzle_velocity:/);
        }
    });

    test('string too long is rejected (mirrors schema/fixtures/invalid/string_too_long.json)', () => {
        const payload = validPayload();
        payload.profile.profileName = 'x'.repeat(51); // schema maxLength is 50
        expect(() => validate(payload)).toThrow(ValidationError);
        try {
            validate(payload);
        } catch (e) {
            expect((e as ValidationError).errors[0]).toMatch(/^profile_name:/);
        }
    });

    test('too few switches is rejected (mirrors schema/fixtures/invalid/too_few_switches.json)', () => {
        const payload = validPayload();
        payload.profile.switches.pop(); // schema minItems is 4
        expect(() => validate(payload)).toThrow(ValidationError);
        try {
            validate(payload);
        } catch (e) {
            expect((e as ValidationError).errors[0]).toMatch(/^switches:/);
        }
    });

    test('c_idx in the undefined 201-254 gap is rejected', () => {
        const payload = validPayload();
        payload.profile.switches[0].cIdx = 210;
        expect(() => validate(payload)).toThrow(ValidationError);
    });

    test('duplicate non-zero mv is rejected (mirrors schema/fixtures/invalid/duplicate_mv.json)', () => {
        const payload = validPayload();
        payload.profile.bcType = BcType.CUSTOM;
        payload.profile.coefRows = [
            { bcCd: 1000, mv: 8000 },
            { bcCd: 1100, mv: 8000 },
        ];
        expect(() => validate(payload)).toThrow(ValidationError);
        try {
            validate(payload);
        } catch (e) {
            expect((e as ValidationError).errors[0]).toMatch(/^coef_rows:/);
        }
    });

    test('mv == 0 may repeat across rows', () => {
        const payload = validPayload();
        payload.profile.bcType = BcType.CUSTOM;
        payload.profile.coefRows = [
            { bcCd: 1000, mv: 0 },
            { bcCd: 1100, mv: 0 },
        ];
        expect(() => validate(payload)).not.toThrow();
    });

    test('abortEarly stops at the first error', () => {
        const payload = validPayload();
        payload.profile.cMuzzleVelocity = 99;
        payload.profile.profileName = 'x'.repeat(51);
        try {
            validate(payload, true);
            throw new Error('expected validate to throw');
        } catch (e) {
            expect((e as ValidationError).errors).toHaveLength(1);
        }
    });
});
