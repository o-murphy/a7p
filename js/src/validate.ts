import validateSchema from './generated/a7p_schema_validator.cjs';
import { CoefRow, Payload, Profile, SwitchProps } from './types.js';
import { ValidationError } from './errors.js';

// Converts the Payload (camelCase, matching the ts-proto/protobuf field
// names) into the plain snake_case JSON shape schema/a7p.schema.json is
// written against -- the same shape MessageToDict(preserving_proto_field_name=True)
// produces in py, and the manual conversion a7p_validator.dart does for dart.
function payloadToSchemaJson(payload: Payload): unknown {
    const p: Profile = payload.profile;
    return {
        profile: {
            profile_name: p.profileName,
            cartridge_name: p.cartridgeName,
            bullet_name: p.bulletName,
            short_name_top: p.shortNameTop,
            short_name_bot: p.shortNameBot,
            caliber: p.caliber,
            device_uuid: p.deviceUuid,
            user_note: p.userNote,
            zero_x: p.zeroX,
            zero_y: p.zeroY,
            sc_height: p.scHeight,
            r_twist: p.rTwist,
            twist_dir: p.twistDir,
            c_muzzle_velocity: p.cMuzzleVelocity,
            c_zero_temperature: p.cZeroTemperature,
            c_t_coeff: p.cTCoeff,
            c_zero_distance_idx: p.cZeroDistanceIdx,
            c_zero_air_temperature: p.cZeroAirTemperature,
            c_zero_air_pressure: p.cZeroAirPressure,
            c_zero_air_humidity: p.cZeroAirHumidity,
            c_zero_w_pitch: p.cZeroWPitch,
            c_zero_p_temperature: p.cZeroPTemperature,
            b_diameter: p.bDiameter,
            b_weight: p.bWeight,
            b_length: p.bLength,
            bc_type: p.bcType,
            switches: (p.switches ?? []).map((sw: SwitchProps) => ({
                c_idx: sw.cIdx,
                distance_from: sw.distanceFrom,
                distance: sw.distance,
                reticle_idx: sw.reticleIdx,
                zoom: sw.zoom,
            })),
            distances: p.distances,
            coef_rows: (p.coefRows ?? []).map((r: CoefRow) => ({
                bc_cd: r.bcCd,
                mv: r.mv,
            })),
        },
    };
}

// ajv reports errors as JSON Pointers rooted at the whole payload (e.g.
// "/profile/switches/0/c_idx"); strip the "/profile" prefix so messages
// read the same as the old yup-based errors did.
function fieldPath(instancePath: string): string {
    let path = instancePath;
    if (path.startsWith('/profile')) {
        path = path.slice('/profile'.length);
    }
    if (path.startsWith('/')) {
        path = path.slice(1);
    }
    return path.length === 0 ? 'payload' : path;
}

// Not expressible in plain JSON Schema (see coef_rows.x-unique-except-zero
// in schema/a7p.schema.json): all 'mv' values must be unique except that
// any number of rows may have mv == 0. Checked separately, same as py's
// schema_validator.py and dart's A7pValidator.
function uniqueMvError(rows: CoefRow[]): string | null {
    const seen = new Set<number>();
    for (const r of rows) {
        if (r.mv !== 0) {
            if (seen.has(r.mv)) {
                return "coef_rows: 'mv' values must be unique, except for mv == 0";
            }
            seen.add(r.mv);
        }
    }
    return null;
}

export const validate = (data: Payload, abortEarly: boolean = false): void => {
    if (!data.profile) {
        throw new ValidationError(['payload: missing profile']);
    }

    const messages: string[] = [];

    const ok = validateSchema(payloadToSchemaJson(data));
    if (!ok) {
        for (const e of validateSchema.errors ?? []) {
            messages.push(`${fieldPath(e.instancePath)}: ${e.message}`);
        }
    }

    const mvError = uniqueMvError(data.profile.coefRows ?? []);
    if (mvError) messages.push(mvError);

    if (messages.length > 0) {
        throw new ValidationError(abortEarly ? [messages[0]] : messages);
    }
};
