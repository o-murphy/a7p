from a7p import profedit_pb2
from a7p.a7p import to_dict
from a7p.yup.yup import obj, array, string, number, mixed

schema = obj().shape({
    'profile': obj().shape({
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
        'zero_x': number().ge(-200000).le(200000).required('Zero X is required'),
        'zero_y': number().ge(-200000).le(200000).integer().required('Zero Y is required'),

        # lists
        'distances': array().of(number().ge(100).le(300000).integer().required()).min(1).max(200),
        'switches': array().of(
            obj().shape({
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


def validate(payload: profedit_pb2.Payload, fail_fast: bool = True):
    data = to_dict(payload)
    schema.validate(data, fail_fast, "<payload>")


if __name__ == '__main__':
    from a7p import load
    from a7p.spec_validator import validate_spec
    from a7p.protovalidate import validate as proto_validate
    import timeit

    with open("../../../example.a7p", 'rb') as f:
        p = load(f, fail_fast=True)


    def v_old():
        validate_spec(p)


    def v_new():
        validate(p)

    def v_pro():
        proto_validate(p)


    num = 10
    told = timeit.timeit(v_old, number=num)

    tnew = timeit.timeit(v_new, number=num)

    tpro = timeit.timeit(v_pro, number=num)

    print(told)
    print(tnew)
    print(tpro)

# schema = obj().shape({
#     'profile': obj().shape({
#         # descriptor
#         'profileName': string().max(50).required('Profile name is required'),
#         'cartridgeName': string().max(50).required('Cartridge name is required'),
#         'bulletName': string().max(50).required('Bullet name is required'),
#         'shortNameTop': string().max(8).required('Short name top is required'),
#         'shortNameBot': string().max(8).required('Short name bottom is required'),
#         'caliber': string().max(50).required('Caliber is required'),
#         'deviceUuid': string().max(50).not_required(),
#         'userNote': string().max(1024).not_required(),
#
#         # zeroing
#         'zeroX': number().ge(-200000).le(200000).integer().required('Zero X is required'),
#         'zeroY': number().ge(-200000).le(200000).integer().required('Zero Y is required'),
#
#         # lists
#         'distances': array().of(number().ge(100).le(300000).integer().required()).min(1).max(200),
#         'switches': array().of(
#             obj().shape({
#                 'cIdx': number().ge(0).le(255).integer().required(),
#                 'distanceFrom': mixed().one_of(['INDEX', 'VALUE']).required(),
#                 'distance': number().ge(100).le(300000).integer().required(),
#                 'reticleIdx': number().ge(0).le(255).integer().required(),
#                 'zoom': number().ge(0).le(255).integer().required(),
#             })
#         ).min(4),
#
#         # rifle
#         'scHeight': number().ge(-5000).le(5000).integer().required(),
#         'rTwist': number().ge(0).le(10000).integer().required(),
#         'twistDir': mixed().one_of(['RIGHT', 'LEFT']).required(),
#
#         # cartridge
#         'cMuzzleVelocity': number().ge(100).le(30000).integer().required(),
#         'cZeroTemperature': number().ge(-100).le(100).integer().required(),
#         'cTCoeff': number().ge(0).le(5000).integer().required(),
#
#         # zero params
#         'cZeroDistanceIdx': number().ge(0).le(255).integer().required(),
#         'cZeroAirTemperature': number().ge(-100).le(100).integer().required(),
#         'cZeroAirPressure': number().ge(3000).le(15000).integer().required(),
#         'cZeroAirHumidity': number().ge(0).le(100).integer().required(),
#         'cZeroWPitch': number().ge(-90).le(90).integer().required(),
#         'cZeroPTemperature': number().ge(-100).le(100).integer().required(),
#
#         # bullet
#         'bDiameter': number().ge(1).le(50000).integer().required(),
#         'bWeight': number().ge(10).le(65535).integer().required(),
#         'bLength': number().ge(1).le(200000).integer().required(),
#
#         # drag model
#         'bcType': mixed().one_of(['G1', 'G7', 'CUSTOM']).required(),
#         'coefRows': array().min(1).max(200).required()
#     }),
# })
