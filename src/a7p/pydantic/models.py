from enum import Enum
from typing import Any

from pydantic import BaseModel, ValidationError, conint, constr, conlist, BeforeValidator, AfterValidator, \
    field_validator
from pydantic_core.core_schema import FieldValidationInfo
from typing_extensions import List, Union, Annotated

from a7p.pydantic.correct import on_restore, trigger_confield_validation


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


def validate_c_zero_distance_idx(value, info: FieldValidationInfo):
    # Retrieve 'distances' from the model's data
    distances = info.data.get('distances')

    # If distances is None, raise an error since validation cannot proceed
    if distances is None:
        raise ValueError("c_zero_distance_idx cannot be valid if distances are invalid or missing")

    # If distances is a list or tuple, and value is not None, validate the index
    if isinstance(distances, (list, tuple)) and value is not None:
        if value >= len(distances):  # Check if index is out of bounds
            raise ValueError(
                f"c_zero_distance_idx must be less than the length of distances (length={len(distances)})"
            )

    # Return the validated value
    return value


def restore_str_len(max_len, default="nil"):
    def decorator(cls: type, value: Any, info: FieldValidationInfo, err: Exception) -> Any:
        if info.context.get('restore'):
            if isinstance(value, str):
                return value[:max_len]
        return default[:max_len]

    return decorator


def restore_default(default):
    def decorator(cls: type, value: Any, info: FieldValidationInfo, err: Exception) -> Any:
        return default

    return decorator


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
    # description params
    profile_name: constr(max_length=50)
    cartridge_name: constr(max_length=50)
    bullet_name: constr(max_length=50)
    short_name_top: constr(max_length=8)
    short_name_bot: constr(max_length=8)
    caliber: constr(max_length=50)
    user_note: constr(max_length=1024)
    device_uuid: constr(max_length=50)

    # zeroing props
    zero_x: conint(ge=-200 * 1000, le=200 * 1000)
    zero_y: conint(ge=-200 * 1000, le=200 * 1000)

    # barrel params
    sc_height: conint(ge=-5000, le=5000)
    r_twist: conint(ge=0, le=100 * 100)
    twist_dir: TwistDir

    # muzzle velocity
    c_muzzle_velocity: conint(ge=-10 * 10, le=3000 * 10)

    # zero environment props
    c_zero_temperature: conint(ge=-100, le=100)
    c_t_coeff: conint(ge=0, le=5 * 1000)
    c_zero_air_temperature: conint(ge=-100, le=100)
    c_zero_air_pressure: conint(ge=300 * 10, le=1500 * 10)
    c_zero_air_humidity: conint(ge=0, le=100)
    c_zero_p_temperature: conint(ge=-100, le=100)
    c_zero_w_pitch: conint(ge=-90 * 10, le=90 * 10)

    # bullet params
    b_diameter: conint(ge=int(0.001 * 1000), le=int(50.0 * 1000))
    b_weight: conint(ge=int(1.0 * 10), le=int(6553.5 * 10))
    b_length: conint(ge=int(0.01 * 1000), le=int(200.0 * 1000))

    bc_type: BCType
    switches: conlist(Switch, min_length=4)
    distances: conlist(conint(ge=int(1.0 * 100), le=int(3000.0 * 100)), min_length=1, max_length=200)
    coef_rows: Annotated[Union[List[BcMvRows], List[CdMaRows]], BeforeValidator(validate_coef_rows_based_on_bc_type)]
    c_zero_distance_idx: Annotated[conint(ge=0, le=200), AfterValidator(validate_c_zero_distance_idx)]


    @field_validator('profile_name',
                     'cartridge_name',
                     'bullet_name',
                     'caliber',
                     mode='before')
    @on_restore(handler=restore_str_len(50))
    def validate_string_50(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('device_uuid', mode='before')
    @on_restore(handler=restore_str_len(50, ""))
    def validate_device_uuid(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('short_name_top',
                     'short_name_bot',
                     mode='before')
    @on_restore(handler=restore_str_len(8))
    def validate_string_8(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('user_note',
                     mode='before')
    @on_restore(handler=restore_str_len(1024))
    def validate_user_note(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('zero_x',
                     'zero_y',
                     'c_zero_air_humidity',
                     'c_zero_w_pitch',
                     mode='before')
    @on_restore(handler=restore_default(0))
    def validate_zero(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('sc_height', mode='before')
    @on_restore(handler=restore_default(90))
    def validate_sc_height(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('c_muzzle_velocity', mode='before')
    @on_restore(handler=restore_default(8000))
    def validate_c_muzzle_velocity(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('c_zero_temperature',
                     'c_zero_air_temperature',
                     'c_zero_p_temperature',
                     mode='before')
    @on_restore(handler=restore_default(15))
    def validate_temperature(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('c_t_coeff', mode='before')
    @on_restore(handler=restore_default(1000))
    def validate_c_t_coeff(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('c_zero_air_pressure', mode='before')
    @on_restore(handler=restore_default(10000))
    def validate_c_zero_pressure(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('b_weight', mode='before')
    @on_restore(handler=restore_default(3000))
    def validate_b_weight(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('b_diameter', mode='before')
    @on_restore(handler=restore_default(1800))
    def validate_b_diameter(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('b_length', mode='before')
    @on_restore(handler=restore_default(338))
    def validate_b_length(cls, value, info: FieldValidationInfo):
        return trigger_confield_validation(cls, value, info)

    @field_validator('twist_dir', mode='before')
    @on_restore(handler=restore_default(TwistDir.RIGHT))
    def validate_twist_dir(cls, value, info: FieldValidationInfo):
        if not value in [TwistDir.RIGHT, TwistDir.LEFT]:
            raise ValueError("Input should be 'RIGHT' or 'LEFT'")
        return trigger_confield_validation(cls, value, info)


class Payload(BaseModel):
    profile: Profile
