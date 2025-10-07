from typing import Dict

from google.protobuf.json_format import MessageToDict
from yupy import (
    mapping,
    array,
    string,
    number,
    mixed,
    union,
    ValidationError,
    Constraint,
    required,
)

from a7p import profedit_pb2

__all__ = ("validate",)

_schema = mapping().shape(
    {
        "profile": required(
            mapping().shape(
                {
                    # descriptor
                    "profile_name": required(
                        string().max(50), "Profile name is required"
                    ),
                    "cartridge_name": required(
                        string().max(50), "Cartridge name is required"
                    ),
                    "bullet_name": required(
                        string().max(50), "Bullet name is required"
                    ),
                    "short_name_top": required(
                        string().max(8), "Short name top is required"
                    ),
                    "short_name_bot": required(
                        string().max(8), "Short name bottom is required"
                    ),
                    "caliber": required(string().max(50), "Caliber is required"),
                    "device_uuid": string().max(50),
                    "user_note": string().max(1024),
                    # zeroing
                    "zero_x": required(
                        number().ge(-200000).le(200000).integer(), "Zero X is required"
                    ),
                    "zero_y": required(
                        number().ge(-200000).le(200000).integer(), "Zero Y is required"
                    ),
                    # lists
                    "distances": required(
                        array()
                        .of(number().ge(100).le(300000).integer())
                        .min(1)
                        .max(200)
                    ),
                    "switches": array()
                    .of(
                        union().one_of(
                            (
                                mapping().shape(
                                    {
                                        "c_idx": required(
                                            number().ge(0).le(255).integer()
                                        ),
                                        "distance_from": required(
                                            mixed().one_of(["VALUE"])
                                        ),
                                        "distance": required(
                                            number().ge(100).le(300000).integer()
                                        ),
                                        "reticle_idx": required(
                                            number().ge(0).le(255).integer()
                                        ),
                                        "zoom": required(
                                            number().ge(0).le(255).integer()
                                        ),
                                    }
                                ),
                                mapping().shape(
                                    {
                                        "c_idx": required(
                                            number().ge(0).le(255).integer()
                                        ),
                                        "distance_from": required(
                                            mixed().one_of(["INDEX"])
                                        ),
                                        "distance": required(
                                            number().ge(0).le(255).integer()
                                        ),
                                        "reticle_idx": required(
                                            number().ge(0).le(255).integer()
                                        ),
                                        "zoom": required(
                                            number().ge(0).le(255).integer()
                                        ),
                                    }
                                ),
                            )
                        )
                    )
                    .min(4),
                    # rifle
                    "sc_height": required(number().ge(-5000).le(5000).integer()),
                    "r_twist": required(number().ge(0).le(10000).integer()),
                    "twist_dir": required(mixed().one_of(["RIGHT", "LEFT"])),
                    # cartridge
                    "c_muzzle_velocity": required(number().ge(100).le(30000).integer()),
                    "c_zero_temperature": required(number().ge(-100).le(100).integer()),
                    "c_t_coeff": required(number().ge(0).le(5000).integer()),
                    # zero params
                    "c_zero_distance_idx": required(number().ge(0).le(255).integer()),
                    "c_zero_air_temperature": required(
                        number().ge(-100).le(100).integer()
                    ),
                    "c_zero_air_pressure": required(
                        number().ge(3000).le(15000).integer()
                    ),
                    "c_zero_air_humidity": required(number().ge(0).le(100).integer()),
                    "c_zero_w_pitch": required(number().ge(-90).le(90).integer()),
                    "c_zero_p_temperature": required(
                        number().ge(-100).le(100).integer()
                    ),
                    # bullet
                    "b_diameter": required(number().ge(1).le(50000).integer()),
                    "b_weight": required(number().ge(10).le(65535).integer()),
                    "b_length": required(number().ge(1).le(200000).integer()),
                    # drag model
                    "bc_type": required(mixed().one_of(["G1", "G7", "CUSTOM"])),
                    "coef_rows": required(array().min(1).max(200)),
                }
            )
        )
    }
)


def _coef_rows_mv_validator(rows):
    if not rows:
        raise ValidationError(
            Constraint("unique_mv", "Coefficient rows must not be empty"),
            invalid_value=rows,
        )
    mv_values = map(lambda x: x["mv"], rows)
    filtered = tuple(filter(lambda mv: mv != 0, mv_values))
    unique = set(filtered)
    if len(unique) != len(filtered):
        raise ValidationError(
            Constraint("unique_mv", "'mv' values must be unique, except for mv == 0"),
            invalid_value=rows,
        )


_coef_rows_std_schema = required(
    array()
    .of(
        mapping().shape(
            {
                "bc_cd": number().ge(0).le(10000).integer(),
                "mv": number().ge(0).le(30000).integer(),
            }
        )
    )
    .min(1)
    .max(5)
    .test(_coef_rows_mv_validator),
    "For G1 or G7, coefRows must contain between 1 and 5 items",
)

_coef_rows_custom_schema = required(
    array()
    .of(
        mapping().shape(
            {
                "bc_cd": number().ge(0).le(10000).integer(),
                "mv": number().ge(0).le(10000).integer(),
            }
        )
    )
    .min(1)
    .max(200)
    .test(_coef_rows_mv_validator),
    "For CUSTOM, coefRows must contain between 1 and 200 items",
)


def validate_coef_rows(data: Dict, fail_fast):
    bc_type = data["profile"]["bc_type"]
    match bc_type:
        case "G1" | "G7":
            _coef_rows_std_schema.validate(
                data["profile"]["coef_rows"], fail_fast, path="~/profile/coef_rows"
            )
        case "CUSTOM":
            _coef_rows_custom_schema.validate(
                data["profile"]["coef_rows"], fail_fast, path="~/profile/coef_rows"
            )


def validate(payload: profedit_pb2.Payload, fail_fast: bool = False):
    data = MessageToDict(
        payload, always_print_fields_with_no_presence=True, preserving_proto_field_name=True
    )
    errors = []
    try:
        _schema.validate(data, fail_fast, "~")
    except ValidationError as err:
        if fail_fast:
            raise err
        errors.append(err)

    try:
        validate_coef_rows(data, fail_fast)
    except ValidationError as err:
        if fail_fast:
            raise err
        errors.append(err)

    if errors:
        raise ValidationError(
            Constraint("invalid payload", "invalid payload"),
            path="~",
            errors=errors,
            invalid_value=payload,
        )
