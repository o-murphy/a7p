from enum import Enum
from typing import Any, get_args

from pydantic import BaseModel, ValidationError, conint, constr, conlist, BeforeValidator, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from typing_extensions import List, Union, Annotated

from a7p.pydantic.correction import on_restore, trigger_confield_validation, pre_validate_conint
from a7p.pydantic.template import PAYLOAD_RECOVERY_SCHEMA



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


LongString = constr(max_length=50)
ShortString = constr(max_length=8)
Text = constr(max_length=1024)

SightHeight = conint(ge=-5000, le=5000)
Twist = conint(ge=0, le=100 * 100)

Velocity = conint(ge=-10 * 10, le=3000 * 10)
TCoeff = conint(ge=0, le=5 * 1000)

Zeroing = conint(ge=-200 * 1000, le=200 * 1000)
Temperature = conint(ge=-100, le=100)
Pressure = conint(ge=300 * 10, le=1500 * 10)
Humidity = conint(ge=0, le=100)
Pitch = conint(ge=-90 * 10, le=90 * 10)

Diameter = conint(ge=int(0.001 * 1000), le=int(50.0 * 1000))
Weight = conint(ge=int(1.0 * 10), le=int(6553.5 * 10))
Length = conint(ge=int(0.01 * 1000), le=int(200.0 * 1000))

SwitchesList = conlist(Switch, min_length=4)
Distance = conint(ge=int(1.0 * 100), le=int(3000.0 * 100))
DistancesList = conlist(Distance, min_length=1, max_length=200)

DistanceIdx = conint(ge=0, le=200, strict=True)
ZeroDistanceIdx = DistanceIdx
# CoefRowsList = Annotated[Union[List[BcMvRows], List[CdMaRows]], BeforeValidator(validate_coef_rows_based_on_bc_type)]
CoefRowsList = Union[List[BcMvRows], List[CdMaRows]]

DEFAULT_DISTANCES = PAYLOAD_RECOVERY_SCHEMA['profile']['distances']
DEFAULT_SWITCHES = PAYLOAD_RECOVERY_SCHEMA['profile']['switches']
DEFAULT_COEF_ROWS = PAYLOAD_RECOVERY_SCHEMA['profile']['coef_rows']


class Profile(BaseModel):
    # description params
    profile_name: LongString
    cartridge_name: LongString
    bullet_name: LongString
    short_name_top: ShortString
    short_name_bot: ShortString
    caliber: LongString
    device_uuid: LongString
    user_note: Text

    # zeroing props
    zero_x: Zeroing
    zero_y: Zeroing

    # barrel params
    sc_height: SightHeight
    r_twist: Twist
    twist_dir: TwistDir

    # muzzle velocity
    c_muzzle_velocity: Velocity
    c_t_coeff: TCoeff

    # zero environment props
    c_zero_temperature: Temperature
    c_zero_air_temperature: Temperature
    c_zero_p_temperature: Temperature
    c_zero_air_pressure: Pressure
    c_zero_air_humidity: Humidity
    c_zero_w_pitch: Pitch

    # bullet params
    b_diameter: Diameter
    b_weight: Weight
    b_length: Length

    switches: SwitchesList
    distances: DistancesList
    c_zero_distance_idx: ZeroDistanceIdx
    bc_type: BCType
    coef_rows: CoefRowsList

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
    @on_restore(handler=restore_default(TwistDir.RIGHT.value))
    def validate_twist_dir(cls, value, info: FieldValidationInfo):
        if value not in [TwistDir.RIGHT, TwistDir.LEFT]:
            raise ValueError("Input should be 'RIGHT' or 'LEFT'")
        return value

    @field_validator('distances', mode='before')
    @on_restore(handler=restore_default(DEFAULT_DISTANCES))
    def validate_distances(cls, value, info: FieldValidationInfo):

        if not isinstance(value, list):
            raise ValueError("Input should be a valid list")

        if len(value) < 1:
            raise ValueError("List should have at least 1 item after validation, not %s" % len(value))
        if len(value) > 200:
            raise ValueError("List should have at most 200 items after validation, not  %s" % len(value))

        if len(value) != len(set(value)):
            repeated_items = list(set([item for item in value if value.count(item) > 1]))

            raise ValueError("Non unique values found in a list %s" % repeated_items)

        validator = pre_validate_conint(*get_args(Distance))

        for d in value:
            try:
                validator(d)
            except (TypeError, ValueError) as err:
                raise ValueError("Invalid values found: %s" % err)

        return value

    @field_validator('c_zero_distance_idx', mode='before')
    @on_restore(handler=restore_default(0))
    def validate_c_zero_distance_idx(cls, value, info: FieldValidationInfo):

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

        return value

    @field_validator('switches', mode='before')
    @on_restore(handler=restore_default(DEFAULT_SWITCHES))
    def validate_switches(cls, value, info: FieldValidationInfo):
        value.append(value[0])
        value[0]['c_idx'] = 500
        if not isinstance(value, list):
            raise ValueError("Input should be a valid list")

        if len(value) < 4:
            raise ValueError("List should have at least 4 item after validation, not %s" % len(value))

        for item in value:
            try:
                Switch.model_validate(item, context=info.context)
            except ValidationError as err:
                raise ValueError("Invalid values found: %s" % err)

        return value

    @field_validator('bc_type', mode='before')
    @on_restore(handler=restore_default(BCType.G7))
    def validate_bc_type(cls, value, info: FieldValidationInfo):
        if value not in [BCType.G1, BCType.G7, BCType.CUSTOM]:
            raise ValueError("Input should be 'G1', 'G7' or 'CUSTOM'")
        return value

    @field_validator('coef_rows', mode='before')
    @on_restore(handler=restore_default(DEFAULT_COEF_ROWS))
    def validate_coef_rows_based_on_bc_type(cls, value, info: FieldValidationInfo):
        # Convert dictionaries to model instances based on bc_type
        bc_type = info.data.get('bc_type')
        value[0]['bc_cd'] = 300000
        try:
            if bc_type in [BCType.G1, BCType.G7]:
                if len(value) < 1:
                    raise ValueError('coef_rows should have at least 1 item when bc_type is %s' % bc_type)
                if len(value) > 5:
                    raise ValueError('coef_rows should have maximum 5 items when bc_type is %s' % bc_type)

                # Ensure coef_rows contains BcMvRows instances
                value = [BcMvRows(**row) if isinstance(row, dict) else row for row in value]
                if not all(isinstance(row, BcMvRows) for row in value):
                    raise ValueError(f'coef_rows must contain BcMvRows when bc_type is %s' % bc_type)
            elif bc_type == BCType.CUSTOM:

                if len(value) < 1:
                    raise ValueError('coef_rows should have at least 1 item when bc_type is {bc_type}')
                if len(value) > 200:
                    raise ValueError('coef_rows should have maximum 200 items when bc_type is {bc_type}')

                # Ensure coef_rows contains CdMaRows instances
                value = [CdMaRows(**row) if isinstance(row, dict) else row for row in value]
                if not all(isinstance(row, CdMaRows) for row in value):
                    raise ValueError(f'coef_rows must contain CdMaRows when bc_type is %s' % bc_type)
            else:
                raise ValueError(f"Unsupported bc_type: %s" % bc_type)

        except ValidationError as e:
            # raise e
            # Handle the validation error gracefully
            raise ValueError(f"Validation error while processing coef_rows for bc_type %s" % bc_type)

        return value


class Payload(BaseModel):
    profile: Profile
