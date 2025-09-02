import { object, string, number, array, mixed, ValidationError } from 'yup';
import { BcType, Payload } from './types.js';
import { InvalidBcTypeError } from './errors.js';


// Define the validation schema for each field
export const schema = object().shape({
    profile: object().shape({
        // descriptor
        profileName: string().max(50).required('Profile name is required'),
        cartridgeName: string().max(50).required('Cartridge name is required'),
        bulletName: string().max(50).required('Bullet name is required'),
        shortNameTop: string().max(8).required('Short name top is required'),
        shortNameBot: string().max(8).required('Short name bottom is required'),
        caliber: string().max(50).required('Caliber is required'),
        deviceUuid: string().max(50).notRequired(),
        userNote: string().max(1024).notRequired(),

        // zeroing
        zeroX: number().min(-200000).max(200000).integer().required('Zero X is required'),
        zeroY: number().min(-200000).max(200000).integer().required('Zero Y is required'),

        // lists
        distances: array().of(number().min(100).max(300000).integer().required()).min(1).max(200),
        switches: array().of(
            object().shape({
                cIdx: number().min(0).max(255).integer().required(),
                distanceFrom: mixed().oneOf(['INDEX', 'VALUE']).required(),
                distance: number().when('distanceFrom', {
                    is: 'VALUE',
                    then: (schema) => schema.min(100).max(300000).integer().required(),
                    otherwise: (schema) => schema.min(0).max(255).integer().required(),
                }),
                reticleIdx: number().min(0).max(255).integer().required(),
                zoom: number().min(0).max(255).integer().required(),
            })
        ).min(4),

        // rifle
        scHeight: number().min(-5000).max(5000).integer().required(),
        rTwist: number().min(0).max(10000).integer().required(),
        twistDir: mixed().oneOf(['RIGHT', 'LEFT']).required(),

        // cartridge
        cMuzzleVelocity: number().min(100).max(30000).integer().required(),
        cZeroTemperature: number().min(-100).max(100).integer().required(),
        cTCoeff: number().min(0).max(5000).integer().required(),

        // zero params
        cZeroDistanceIdx: number().min(0).max(255).integer().required(),
        cZeroAirTemperature: number().min(-100).max(100).integer().required(),
        cZeroAirPressure: number().min(3000).max(15000).integer().required(),
        cZeroAirHumidity: number().min(0).max(100).integer().required(),
        cZeroWPitch: number().min(-90).max(90).integer().required(),
        cZeroPTemperature: number().min(-100).max(100).integer().required(),

        // bullet
        bDiameter: number().min(1).max(50000).integer().required(),
        bWeight: number().min(10).max(65535).integer().required(),
        bLength: number().min(1).max(200000).integer().required(),

        // drag model
        bcType: mixed().oneOf([BcType.G1, BcType.G7, BcType.CUSTOM]).required(),
        coefRows: array().min(1).max(200).required()
    }),
});

// Schema for coefRows when bcType is 'G1' or 'G7'
const coefRowsStandard = array().of(
    object().shape({
        bcCd: number().min(0).max(10000).integer(),
        mv: number().min(0).max(30000).integer(),
    })
).min(1).max(5).required('For G1 or G7, coefRows must contain between 1 and 5 items')
    .test('unique-mv', 'mv values must be unique, except for mv == 0', (value) => {
        if (!value) {
            return false
        }
        const mvValues = value.map((row) => row.mv);
        const filteredMvValues = mvValues.filter(mv => mv !== 0); // Exclude zeros for uniqueness check
        const uniqueMvValues = new Set(filteredMvValues);
        return filteredMvValues.length === uniqueMvValues.size;
    });

// Schema for coefRows when bcType is 'CUSTOM'
const coefRowsCustom = array().of(
    object().shape({
        bcCd: number().min(0).max(10000).integer(),
        mv: number().min(0).max(10000).integer()
    })
).min(1).max(200).required('For CUSTOM, coefRows must contain between 1 and 200 items')
    .test('unique-mv', 'mv values must be unique, except for mv == 0', (value) => {
        if (!value) {
            return false
        }
        const mvValues = value.map((row) => row.mv);
        const filteredMvValues = mvValues.filter(mv => mv !== 0); // Exclude zeros for uniqueness check
        const uniqueMvValues = new Set(filteredMvValues);
        return filteredMvValues.length === uniqueMvValues.size;
    });


export const validate = (data: Payload, abortEarly: boolean = false): void => {
    try {
        const validData = schema.validateSync(data, { abortEarly });

        switch (validData.profile.bcType) {
            case BcType.G1:
            case BcType.G7:
                coefRowsStandard.validateSync(data.profile?.coefRows, { abortEarly });
                break;
            case BcType.CUSTOM:
                coefRowsCustom.validateSync(data.profile?.coefRows, { abortEarly });
                break;
            default:
                throw new InvalidBcTypeError(data.profile?.bcType);
        }
    } catch (error: any) {
        if (error.name === "ValidationError") {
            const yupErrors = error.errors ?? [error.message];
            throw new ValidationError(yupErrors);
        } else {
            throw error;
        }
    }
};
