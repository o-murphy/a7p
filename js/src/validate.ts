import * as yup from 'yup';
import { BcType, Payload } from './types.js';
import { InvalidBcTypeError } from './errors.js';


// Define the validation schema for each field
export const schema = yup.object().shape({
    profile: yup.object().shape({
        // descriptor
        profileName: yup.string().max(50).required('Profile name is required'),
        cartridgeName: yup.string().max(50).required('Cartridge name is required'),
        bulletName: yup.string().max(50).required('Bullet name is required'),
        shortNameTop: yup.string().max(8).required('Short name top is required'),
        shortNameBot: yup.string().max(8).required('Short name bottom is required'),
        caliber: yup.string().max(50).required('Caliber is required'),
        deviceUuid: yup.string().max(50).notRequired(),
        userNote: yup.string().max(1024).notRequired(),

        // zeroing
        zeroX: yup.number().min(-200000).max(200000).integer().required('Zero X is required'),
        zeroY: yup.number().min(-200000).max(200000).integer().required('Zero Y is required'),

        // lists
        distances: yup.array().of(yup.number().min(100).max(300000).integer().required()).min(1).max(200),
        switches: yup.array().of(
            yup.object().shape({
                cIdx: yup.number().min(0).max(255).integer().required(),
                distanceFrom: yup.mixed().oneOf(['INDEX', 'VALUE']).required(),
                distance: yup.number().min(100).max(300000).integer().required(),
                reticleIdx: yup.number().min(0).max(255).integer().required(),
                zoom: yup.number().min(0).max(255).integer().required(),
            })
        ).min(4),

        // rifle
        scHeight: yup.number().min(-5000).max(5000).integer().required(),
        rTwist: yup.number().min(0).max(10000).integer().required(),
        twistDir: yup.mixed().oneOf(['RIGHT', 'LEFT']).required(),

        // cartridge
        cMuzzleVelocity: yup.number().min(100).max(30000).integer().required(),
        cZeroTemperature: yup.number().min(-100).max(100).integer().required(),
        cTCoeff: yup.number().min(0).max(5000).integer().required(),

        // zero params
        cZeroDistanceIdx: yup.number().min(0).max(255).integer().required(),
        cZeroAirTemperature: yup.number().min(-100).max(100).integer().required(),
        cZeroAirPressure: yup.number().min(3000).max(15000).integer().required(),
        cZeroAirHumidity: yup.number().min(0).max(100).integer().required(),
        cZeroWPitch: yup.number().min(-90).max(90).integer().required(),
        cZeroPTemperature: yup.number().min(-100).max(100).integer().required(),

        // bullet
        bDiameter: yup.number().min(1).max(50000).integer().required(),
        bWeight: yup.number().min(10).max(65535).integer().required(),
        bLength: yup.number().min(1).max(50000).integer().required(),

        // drag model
        bcType: yup.mixed().oneOf([BcType.G1, BcType.G7, BcType.CUSTOM]).required(),
        coefRows: yup.array().min(1).max(200).required()
    }),
});

// Schema for coefRows when bcType is 'G1' or 'G7'
const coefRowsStandard = yup.array().of(
    yup.object().shape({
        bcCd: yup.number().min(0).max(10000).integer(),
        mv: yup.number().min(0).max(10000).integer(),
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
const coefRowsCustom = yup.array().of(
    yup.object().shape({
        bcCd: yup.number().min(0).max(100000).integer(),
        mv: yup.number().min(0).max(100000).integer()
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
            throw new yup.ValidationError(yupErrors);
        } else {
            throw error;
        }
    }
};
