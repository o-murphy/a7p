from google.protobuf.json_format import MessageToDict
from yupy import mapping, array, string, number, mixed, ValidationError, Constraint

from a7p import profedit_pb2

__all__ = (
    'validate',
)

_schema = mapping().shape({
    'profile': mapping().shape({
        # descriptor
        'profile_name': string().max(50).required('Profile name is required'),
        'cartridge_name': string().max(50).required('Cartridge name is required'),
        'bullet_name': string().max(50).required('Bullet name is required'),
        'short_name_top': string().max(8).required('Short name top is required'),
        'short_name_bot': string().max(8).required('Short name bottom is required'),
        'caliber': string().max(50).required('Caliber is required'),
        'device_uuid': string().max(50).not_required(),
        'user_note': string().max(1024).not_required(),

        # zeroing
        'zero_x': number().ge(-200000).le(200000).integer().required('Zero X is required'),
        'zero_y': number().ge(-200000).le(200000).integer().required('Zero Y is required'),

        # lists
        'distances': array().of(number().ge(100).le(300000).integer().required()).min(1).max(200),
        'switches': array().of(
            mapping().shape({
                'c_idx': number().ge(0).le(255).integer().required(),
                'distance_from': mixed().one_of(['INDEX', 'VALUE']).required(),
                'distance': number().ge(100).le(300000).integer().required(),
                'reticle_idx': number().ge(0).le(255).integer().required(),
                'zoom': number().ge(0).le(255).integer().required(),
            })
        ).min(4),

        # rifle
        'sc_height': number().ge(-5000).le(5000).integer().required(),
        'r_twist': number().ge(0).le(10000).integer().required(),
        'twist_dir': mixed().one_of(['RIGHT', 'LEFT']).required(),

        # cartridge
        'c_muzzle_velocity': number().ge(100).le(30000).integer().required(),
        'c_zero_temperature': number().ge(-100).le(100).integer().required(),
        'c_t_coeff': number().ge(0).le(5000).integer().required(),

        # zero params
        'c_zero_distance_idx': number().ge(0).le(255).integer().required(),
        'c_zero_air_temperature': number().ge(-100).le(100).integer().required(),
        'c_zero_air_pressure': number().ge(3000).le(15000).integer().required(),
        'c_zero_air_humidity': number().ge(0).le(100).integer().required(),
        'c_zero_w_pitch': number().ge(-90).le(90).integer().required(),
        'c_zero_p_temperature': number().ge(-100).le(100).integer().required(),

        # bullet
        'b_diameter': number().ge(1).le(50000).integer().required(),
        'b_weight': number().ge(10).le(65535).integer().required(),
        'b_length': number().ge(1).le(200000).integer().required(),

        # drag model
        'bc_type': mixed().one_of(['G1', 'G7', 'CUSTOM']).required(),
        'coef_rows': array().min(1).max(200).required()
    }),
})


def _coef_rows_mv_validator(rows):
    if not rows:
        raise ValidationError(
            Constraint(
                'unique_mv',
                'Coefficient rows must not be empty'
            ),
            invalid_value=rows
        )
    mv_values = map(lambda x: x['mv'], rows)
    filtered = tuple(filter(lambda mv: mv != 0, mv_values))
    unique = set(filtered)
    if len(unique) != len(filtered):
        raise ValidationError(
            Constraint(
                'unique_mv',
                "'mv' values must be unique, except for mv == 0"
            ),
            invalid_value=rows
        )

_coef_rows_std_schema = array().of(
    mapping().shape({
        'bc_cd': number().ge(0).le(10000).integer(),
        'mv': number().ge(0).le(30000).integer(),
    })
).min(1).max(5).required(
    'For G1 or G7, coefRows must contain between 1 and 5 items'
).test(_coef_rows_mv_validator)

_coef_rows_custom_schema = array().of(
    mapping().shape({
        'bc_cd': number().ge(0).le(10000).integer(),
        'mv': number().ge(0).le(10000).integer()
    })
).min(1).max(200).required(
    'For CUSTOM, coefRows must contain between 1 and 200 items'
).test(_coef_rows_mv_validator)


def validate(payload: profedit_pb2.Payload, fail_fast: bool = False):
    data = MessageToDict(payload,
                         including_default_value_fields=True,
                         preserving_proto_field_name=True)
    errors = []
    try:
        _schema.validate(data, fail_fast, "~")
    except ValidationError as err:
        if fail_fast:
            raise err
        errors.append(err)

    try:
        bc_type = data['profile']['bc_type']
        if bc_type in {'G1', 'G7'}:
            _coef_rows_std_schema.validate(data['profile']['coef_rows'], fail_fast,
                                           path='~/profile/coef_rows')
        elif bc_type == 'CUSTOM':
            _coef_rows_custom_schema.validate(data['profile']['coef_rows'], fail_fast,
                                              path='~/profile/coef_rows')
    except ValidationError as err:
        if fail_fast:
            raise err
        errors.append(err)

    if errors:
        raise ValidationError(Constraint(
            "invalid payload",
            "invalid payload"
        ), path="~", errors=errors, invalid_value=payload)


