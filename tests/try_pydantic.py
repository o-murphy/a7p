from typing import List, Union

from pydantic_core.core_schema import FieldValidationInfo

import a7p
from pydantic import BaseModel, ValidationError, conint, constr, conlist, field_validator, model_validator
from enum import Enum

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
    cIdx: int
    zoom: conint(ge=0, le=6)
    distance: conint(ge=int(1.0 * 100), le=int(3000.0 * 100))
    reticleIdx: conint(ge=0, le=255)
    distanceFrom: Union[int, str]

    @field_validator("cIdx", mode="before")
    def check_cIdx(cls, v):
        if not (0 <= v <= 200 or v == 255):
            raise ValueError('cIdx must be between 0 and 200, or exactly 255')
        # assert 0 <= v <= 200 or v == 255
        return v

    @field_validator("distanceFrom")
    def validate_distance_from(cls, v):
        if isinstance(v, int):
            # Ensure the integer is within the allowed range
            if not (0 <= v <= 255):
                raise ValueError("distanceFrom must be between 0 and 255 if it's an integer.")
        elif isinstance(v, str):
            # Ensure the string is 'VALUE'
            if v != 'VALUE':
                raise ValueError("distanceFrom must be 'VALUE' if it's a string.")
        else:
            raise ValueError("distanceFrom must be either an integer in range 0-255 or the string 'VALUE'.")

        return v


class CoefRows(BaseModel):
    bcCd: int
    mv: int


class CdMaRows(CoefRows):
    bcCd: conint(ge=int(0.0 * 10000), le=int(10.0 * 10000))
    mv: conint(ge=int(0.0 * 10000), le=int(10.0 * 10000))


class BcMvRows(CoefRows):
    bcCd: conint(ge=int(0.0 * 10000), le=int(10.0 * 10000))
    mv: conint(ge=int(0.0 * 10), le=int(3000.0 * 10))


class ProfileValidationError(ValueError):
    def __init__(self, message: str, errors: str):
        super().__init__(message)
        self.errors = errors


class Profile(BaseModel):
    profileName: constr(max_length=50)
    cartridgeName: constr(max_length=50)
    bulletName: constr(max_length=50)
    shortNameTop: constr(max_length=8)
    shortNameBot: constr(max_length=8)
    userNote: constr(max_length=1024)
    zeroX: conint(ge=-200 * 1000, le=200 * 1000)
    zeroY: conint(ge=-200 * 1000, le=200 * 1000)
    scHeight: conint(ge=-5000, le=5000)
    rTwist: conint(ge=0, le=100 * 100)
    cMuzzleVelocity: conint(ge=-10 * 10, le=3000 * 10)
    cZeroTemperature: conint(ge=-100, le=100)
    cTCoeff: conint(ge=0, le=5 * 1000)
    cZeroAirTemperature: conint(ge=-100, le=100)
    cZeroAirPressure: conint(ge=300 * 10, le=1500 * 10)
    cZeroAirHumidity: conint(ge=0, le=100)
    cZeroPTemperature: conint(ge=-100, le=100)
    bDiameter: conint(ge=int(0.001 * 1000), le=int(50.0 * 1000))
    bWeight: conint(ge=int(1.0 * 10), le=int(6553.5 * 10))
    bLength: conint(ge=int(0.01 * 1000), le=int(200.0 * 1000))
    bcType: BCType
    switches: conlist(Switch, min_length=4)
    distances: conlist(conint(ge=int(1.0 * 100), le=int(3000.0 * 100)), min_length=1, max_length=200)
    coefRows: Union[List[BcMvRows], List[CdMaRows]]
    caliber: constr(max_length=50)
    cZeroDistanceIdx: conint(ge=0, le=200)
    cZeroWPitch: conint(ge=-90 * 10, le=90 * 10)
    twistDir: TwistDir
    deviceUuid: constr(max_length=50)

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

    @field_validator("coefRows", mode="before")
    def validate_coefRows_based_on_bcType(cls, v, info: FieldValidationInfo):
        # Convert dictionaries to model instances based on bcType
        bc_type = info.data.get('bcType')

        try:
            if bc_type == BCType.G1 or bc_type == BCType.G7:
                # Ensure coefRows contains BcMvRows instances
                v = [BcMvRows(**row) if isinstance(row, dict) else row for row in v]
                if not all(isinstance(row, BcMvRows) for row in v):
                    raise ValueError(f'coefRows must contain BcMvRows when bcType is {bc_type}')
            elif bc_type == BCType.CUSTOM:
                # Ensure coefRows contains CdMaRows instances
                v = [CdMaRows(**row) if isinstance(row, dict) else row for row in v]
                if not all(isinstance(row, CdMaRows) for row in v):
                    raise ValueError(f'coefRows must contain CdMaRows when bcType is {bc_type}')
            else:
                raise ValueError(f"Unsupported bcType: {bc_type}")

        except ValidationError as e:
            # raise e
            # Handle the validation error gracefully
            raise ProfileValidationError(f"Validation error while processing coefRows for bcType {bc_type}", str(e))

        return v


class Payload(BaseModel):
    profile: Profile


if __name__ == "__main__":
    from pprint import pprint

    with open("broken.a7p", 'rb') as fp:
        try:
            payload = a7p.load(fp, validate_=True)
        except A7PValidationError as err:
            for v in err.violations:
                print(v.format())

            payload = err.payload
            payload.profile.c_zero_distance_idx = 200

            data = a7p.to_dict(payload)
            print("d", len([v for v in payload.profile.distances]))
            try:
                payload = Payload(**data)
                pprint(payload)
            except ValidationError as e:
                print(e)
