from enum import Enum
from typing import List, Union

from google.protobuf.json_format import MessageToDict
from pydantic import BaseModel, ValidationError, conint, constr, conlist, field_validator
from pydantic_core.core_schema import FieldValidationInfo

import a7p
from a7p.exceptions import A7PValidationError


class BCType(Enum):
    G1 = "G1"
    G7 = "G7"
    CUSTOM = "CUSTOM"


class TwistDir(Enum):
    RIGHT = "RIGHT"
    LEFT = "LEFT"


def snake_to_camel(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class Switch(BaseModel):
    c_idx: int
    zoom: conint(ge=0, le=6)
    distance: conint(ge=int(1.0 * 100), le=int(3000.0 * 100))
    reticle_idx: conint(ge=0, le=255)
    distance_from: Union[int, str]

    @field_validator("c_idx", mode="before")
    def check_cIdx(cls, v):
        if not (0 <= v <= 200 or v == 255):
            raise ValueError('cIdx must be between 0 and 200, or exactly 255')
        # assert 0 <= v <= 200 or v == 255
        return v

    @field_validator("distance_from")
    def validate_distance_from(cls, v):
        if isinstance(v, int):
            # Ensure the integer is within the allowed range
            if not (0 <= v <= 255):
                raise ValueError("distanceFrom must be between 0 and 255 if it's an integer.")
        elif isinstance(v, str):
            # Ensure the string is 'VALUE'
            if v.lower() not in ['value', 'index']:
                raise ValueError("distanceFrom must be 'VALUE' if it's a string.")
        else:
            raise ValueError("distanceFrom must be either an integer in range 0-255 or the string 'VALUE' or 'INDEX'.")

        return v


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
    coef_rows: Union[List[BcMvRows], List[CdMaRows]]
    # coef_rows: List[CoefRows]
    caliber: constr(max_length=50)
    c_zero_distance_idx: conint(ge=0, le=200)
    c_zero_w_pitch: conint(ge=-90 * 10, le=90 * 10)
    twist_dir: TwistDir
    device_uuid: constr(max_length=50)

    # # FIXME: do not work as expected
    # @model_validator(mode="before")
    # def validate_cZeroDistanceIdx(cls, values):
    #     distances = values.get('distances')
    #     cZeroDistanceIdx = values.get('cZeroDistanceIdx')
    #     if isinstance(distances, (list, tuple)) and cZeroDistanceIdx is not None:
    #         print("V", len(distances), cZeroDistanceIdx, cZeroDistanceIdx >= len(distances))
    #
    #         if cZeroDistanceIdx >= len(distances):
    #             print("V", len(distances), cZeroDistanceIdx)
    #             raise ValueError(f"cZeroDistanceIdx must be less than the length of distances (length={len(distances)})")
    #
    #     return values

    @field_validator("coef_rows", mode="before")
    def validate_coefRows_based_on_bcType(cls, v, info: FieldValidationInfo):
        # Convert dictionaries to model instances based on bcType
        bc_type = info.data.get('bc_type')
        print(bc_type)
        try:
            if bc_type == BCType.G1 or bc_type == BCType.G7:
                if len(v) < 1:
                    raise ValueError('coef_rows should have at least 1 item when bc_type is {bc_type}')
                if len(v) > 5:
                    raise ValueError('coef_rows should have maximum 5 items when bc_type is {bc_type}')

                # Ensure coefRows contains BcMvRows instances
                v = [BcMvRows(**row) if isinstance(row, dict) else row for row in v]
                if not all(isinstance(row, BcMvRows) for row in v):
                    raise ValueError(f'coef_rows must contain BcMvRows when bc_type is {bc_type}')
            elif bc_type == BCType.CUSTOM:

                if len(v) < 1:
                    raise ValueError('coef_rows should have at least 1 item when bc_type is {bc_type}')
                if len(v) > 200:
                    raise ValueError('coef_rows should have maximum 200 items when bc_type is {bc_type}')

                # Ensure coefRows contains CdMaRows instances
                v = [CdMaRows(**row) if isinstance(row, dict) else row for row in v]
                if not all(isinstance(row, CdMaRows) for row in v):
                    raise ValueError(f'coef_rows must contain CdMaRows when bc_type is {bc_type}')
            else:
                raise ValueError(f"Unsupported bc_type: {bc_type}")

        except ValidationError as e:
            # raise e
            # Handle the validation error gracefully
            raise ProfileValidationError(f"Validation error while processing coefRows for bcType {bc_type}", str(e))

        return v


class Payload(BaseModel):
    profile: Profile


if __name__ == "__main__":
    from pprint import pprint

    def set_value_by_field_path(payload, field_path, value):
        """
        Sets a value in a nested protobuf message based on a field path.

        Args:
            payload: The protobuf message object.
            field_path: The path to the field (can be a string or a list of field names).
            value: The value to set.
        """
        # Convert string path to list if it's a string
        if isinstance(field_path, str):
            field_path = field_path.split('.')

        # Traverse the message to the second-to-last field in the path
        attr = payload
        for field in field_path[:-1]:
            if hasattr(attr, field):
                attr = getattr(attr, field)
            else:
                raise AttributeError(f"Field '{field}' not found in {attr.__class__.__name__}")

        # Set the value at the last field in the path
        last_field = field_path[-1]
        if hasattr(attr, last_field):
            setattr(attr, last_field, value)
        else:
            raise AttributeError(f"Field '{last_field}' not found in {attr.__class__.__name__}")

    with open("broken.a7p", 'rb') as fp:
        try:
            payload = a7p.load(fp, validate_=True)
        except A7PValidationError as err:
            for v in err.all_violations:
                print(v.format())
            payload = err.payload
        finally:
            payload.profile.distances[:] = [100000000]
            data = MessageToDict(
                payload,
                including_default_value_fields=True,
                preserving_proto_field_name=True
            )
            print("Pydantic validation there")
            data['profile']['bc_type'] = 'CUSTOM'
            data['profile']['sc_height'] = 'invalid'
            try:
                Payload.model_validate(data)
            except ValidationError as err:
                print("Errors", len(err.errors()))
                for e in err.errors():
                    pprint(e)

                    # attr = payload
                    # for key in e['loc']:
                    #     if isinstance(key, str):
                    #         attr = getattr(attr, key)
                    #     elif isinstance(key, int):
                    #         attr = attr[key]

                    field_path = e['loc']
                    if isinstance(e['loc'][-1], int):
                        field_path = e['loc'][:-1]

                    last_key = field_path[-1]
                    if last_key == 'c_muzzle_velocity':
                        set_value_by_field_path(payload, ".".join([str(i) for i in e['loc']]), 8000)
                    if last_key == 'distance':
                        set_value_by_field_path(payload, ".".join([str(i) for i in e['loc']]), [1000])
                    else:
                        print(e['loc'])

                data = MessageToDict(
                    payload,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True
                )
                print(data['profile']['distances'])
                try:
                    Payload.model_validate(data)
                except ValidationError as err:
                    print("Errors", len(err.errors()))
                    for e in err.errors():
                        pprint(e)
