from enum import Enum

from typing_extensions import List, Union, Annotated

from pydantic import BaseModel, ValidationError, conint, constr, conlist, BeforeValidator
from pydantic_core.core_schema import FieldValidationInfo


def validate_coef_rows_based_on_bc_type(v, info: FieldValidationInfo):
    # Convert dictionaries to model instances based on bc_type
    bc_type = info.data.get('bc_type')

    try:
        if bc_type == BCType.G1 or bc_type == BCType.G7:
            if len(v) < 1:
                raise ValueError('coef_rows should have at least 1 item when bc_type is {bc_type}')
            if len(v) > 5:
                raise ValueError('coef_rows should have maximum 5 items when bc_type is {bc_type}')

            # Ensure coef_rows contains BcMvRows instances
            v = [BcMvRows(**row) if isinstance(row, dict) else row for row in v]
            if not all(isinstance(row, BcMvRows) for row in v):
                raise ValueError(f'coef_rows must contain BcMvRows when bc_type is {bc_type}')
        elif bc_type == BCType.CUSTOM:

            if len(v) < 1:
                raise ValueError('coef_rows should have at least 1 item when bc_type is {bc_type}')
            if len(v) > 200:
                raise ValueError('coef_rows should have maximum 200 items when bc_type is {bc_type}')

            # Ensure coef_rows contains CdMaRows instances
            v = [CdMaRows(**row) if isinstance(row, dict) else row for row in v]
            if not all(isinstance(row, CdMaRows) for row in v):
                raise ValueError(f'coef_rows must contain CdMaRows when bc_type is {bc_type}')
        else:
            raise ValueError(f"Unsupported bc_type: {bc_type}")

    except ValidationError as e:
        # raise e
        # Handle the validation error gracefully
        raise ProfileValidationError(f"Validation error while processing coef_rows for bc_type {bc_type}", str(e))

    return v


def validate_c_idx(v):
    if not (0 <= v <= 200 or v == 255):
        raise ValueError('c_idx must be between 0 and 200, or exactly 255')
    # assert 0 <= v <= 200 or v == 255
    return v


def validate_distance_from(v):
    if isinstance(v, int):
        # Ensure the integer is within the allowed range
        if not (0 <= v <= 255):
            raise ValueError("distance_from must be between 0 and 255 if it's an integer.")
    elif isinstance(v, str):
        # Ensure the string is 'VALUE'
        if v.lower() not in ['value', 'index']:
            raise ValueError("distance_from must be 'VALUE' if it's a string.")
    else:
        raise ValueError("distance_from must be either an integer in range 0-255 or the string 'VALUE' or 'INDEX'.")

    return v


class BCType(Enum):
    G1 = "G1"
    G7 = "G7"
    CUSTOM = "CUSTOM"


class TwistDir(Enum):
    RIGHT = "RIGHT"
    LEFT = "LEFT"


class Switch(BaseModel):
    c_idx: Annotated[int, BeforeValidator(validate_c_idx)]
    zoom: conint(ge=0, le=6)
    distance: conint(ge=int(1.0 * 100), le=int(3000.0 * 100))
    reticle_idx: conint(ge=0, le=255)
    distance_from: Annotated[Union[int, str], BeforeValidator(validate_distance_from)]


class CoefRows(BaseModel):
    bc_cd: int
    mv: int


class CdMaRows(CoefRows):
    bc_cd: conint(ge=int(0.0 * 10000), le=int(10.0 * 10000))
    mv: conint(ge=int(0.0 * 10000), le=int(10.0 * 10000))


class BcMvRows(CoefRows):
    bc_cd: conint(ge=int(0.0 * 10000), le=int(10.0 * 10000))
    mv: conint(ge=int(0.0 * 10), le=int(3000.0 * 10))


class ProfileValidationError(ValueError):
    def __init__(self, message: str, errors: str):
        super().__init__(message)
        self.errors = errors


class Profile(BaseModel):
    profile_name: constr(max_length=50)
    cartridge_name: constr(max_length=50)
    bullet_name: constr(max_length=50)
    short_name_top: constr(max_length=8)
    short_name_bot: constr(max_length=8)
    user_note: constr(max_length=1024)
    zero_x: conint(ge=-200 * 1000, le=200 * 1000)
    zero_y: conint(ge=-200 * 1000, le=200 * 1000)
    sc_height: conint(ge=-5000, le=5000)
    r_twist: conint(ge=0, le=100 * 100)
    c_muzzle_velocity: conint(ge=-10 * 10, le=3000 * 10)
    c_zero_temperature: conint(ge=-100, le=100)
    c_t_coeff: conint(ge=0, le=5 * 1000)
    c_zero_air_temperature: conint(ge=-100, le=100)
    c_zero_air_pressure: conint(ge=300 * 10, le=1500 * 10)
    c_zero_air_humidity: conint(ge=0, le=100)
    c_zero_p_temperature: conint(ge=-100, le=100)
    b_diameter: conint(ge=int(0.001 * 1000), le=int(50.0 * 1000))
    b_weight: conint(ge=int(1.0 * 10), le=int(6553.5 * 10))
    b_length: conint(ge=int(0.01 * 1000), le=int(200.0 * 1000))
    bc_type: BCType
    switches: conlist(Switch, min_length=4)
    distances: conlist(conint(ge=int(1.0 * 100), le=int(3000.0 * 100)), min_length=1, max_length=200)
    coef_rows: Annotated[Union[List[BcMvRows], List[CdMaRows]], BeforeValidator(validate_coef_rows_based_on_bc_type)]
    caliber: constr(max_length=50)
    c_zero_distance_idx: conint(ge=0, le=200)
    c_zero_w_pitch: conint(ge=-90 * 10, le=90 * 10)
    twist_dir: TwistDir
    device_uuid: constr(max_length=50)

    # # FIXME: do not work as expected
    # @model_validator(mode="before")
    # def validate_c_zero_distance_idx(cls, values):
    #     distances = values.get('distances')
    #     c_zero_distance_idx = values.get('c_zero_distance_idx')
    #     print(distances, c_zero_distance_idx)
    #     if isinstance(distances, (list, tuple)) and c_zero_distance_idx is not None:
    #         if c_zero_distance_idx >= len(distances):
    #             raise ValueError(f"c_zero_distance_idx must be less than the length of distances (length={len(distances)})")
    #
    #     return values


def validate_and_correct_range(value: int, min_value: int, max_value: int) -> int:
    """Ensure value is within valid range, correcting if necessary."""
    return max(min_value, min(value, max_value))


class Payload(BaseModel):
    profile: Profile
