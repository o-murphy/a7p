import pathlib
import re
from dataclasses import dataclass
from typing import Callable, Any

from a7p import profedit_pb2, A7PFile, A7PDataError

__all__ = ['Validator', 'Criterion', 'A7PValidationError']


@dataclass
class Criterion:
    key: str
    validate: Callable[[Any], bool]


class A7PValidationError(A7PDataError):
    ...


class Validator:
    def __init__(self):
        self.criteria = {}

        self.register(_check_profile_name)
        self.register(_check_cartridge_name)
        self.register(_check_caliber)
        self.register(_check_bullet_name)
        self.register(_check_device_uuid)
        self.register(_check_short_name_top)
        self.register(_check_short_name_bot)
        self.register(_check_user_note)
        self.register(_check_zero_x)
        self.register(_check_zero_y)
        self.register(_check_sc_height)
        self.register(_check_r_twist)
        self.register(_check_c_muzzle_velocity)
        self.register(_check_c_zero_temperature)
        self.register(_check_c_t_coeff)
        self.register(_check_c_zero_air_temperature)
        self.register(_check_c_zero_air_pressure)
        self.register(_check_c_zero_air_humidity)
        self.register(_check_c_zero_p_temperature)
        self.register(_check_c_zero_w_pitch)
        self.register(_check_c_zero_b_length)
        self.register(_check_c_zero_b_weight)
        self.register(_check_c_zero_b_diameter)
        self.register(_check_distance)

        self.register(_check_bc_type)

    def register(self, criteria: Criterion):
        self.criteria[criteria.key] = criteria

    def unregister(self, key: str):
        self.criteria.pop(key, None)

    def  get_criteria_by_path(self, path: pathlib.Path) -> Criterion:
        raise NotImplementedError

    def _validate(self, data: any, path: pathlib.Path = pathlib.Path("~/")):
        if isinstance(data, dict):
            # If `data` is a dictionary, iterate over its key-value pairs
            for key, value in data.items():
                current_path = path / key
                self._validate(value, current_path)

        elif isinstance(data, list):
            # If `data` is a list, iterate over its elements
            for i, item in enumerate(data):
                item_path = path / f"[{i}]"
                self._validate(item, item_path)

        else:
            # For scalar values, perform validation
            key = path.name  # Get the current key from the path
            criterion = self.criteria.get(key, None)
            if criterion is None:
                criterion = self.get_criteria_by_path(path)
            if criterion is None:
                print(f"NoValidatorsRegistered\t{key}\t{path}\t{data if isinstance(data, (int, float, str, bool)) else None}")
            if isinstance(criterion, Criterion):
                if not criterion.validate(data):
                    raise A7PValidationError(f"{path.as_posix()} has not valid value: {data}")

    def validate(self, payload: profedit_pb2.Payload):
        data = A7PFile.to_dict(payload)
        print(payload.profile.zero_x)
        self._validate(data)


_check_profile_name = Criterion(
    "profileName", lambda x: len(x) < 50
)

_check_cartridge_name = Criterion(
    "cartridgeName", lambda x: len(x) < 50
)

_check_caliber = Criterion(
    "caliber", lambda x: len(x) < 50
)

_check_bullet_name = Criterion(
    "bulletName", lambda x: len(x) < 50
)

_check_device_uuid = Criterion(
    "deviceUUID", lambda x: len(x) < 50
)

_check_short_name_top = Criterion(
    "shortNameTop", lambda x: len(x) < 8
)

_check_short_name_bot = Criterion(
    "shortNameBot", lambda x: len(x) < 8
)

_check_user_note = Criterion(
    "userNote", lambda x: len(x) < 1024
)

_check_zero_x = Criterion(
    "zeroX", lambda x: -200.0 <= x / 1000 <= 200.0
)

_check_zero_y = Criterion(
    "zeroY", lambda x: -200.0 <= x / 1000 <= 200.0
)

_check_sc_height = Criterion(
    "scHeight", lambda x: -5000.0 <= x / 1000 <= 5000.0
)

_check_r_twist = Criterion(
    "rTwist", lambda x: 0.0 <= x / 10 <= 100.0
)

_check_c_muzzle_velocity = Criterion(
    "cMuzzleVelocity", lambda x: 10.0 <= x / 10 <= 3000.0
)

_check_c_zero_temperature = Criterion(
    "cZeroTemperature", lambda x: -100.0 <= x <= 100.0
)

_check_c_t_coeff = Criterion(
    "cTCoeff", lambda x: 0.0 <= x / 1000 <= 5.0
)

_check_c_zero_air_temperature = Criterion(
    "cZeroAirTemperature", lambda x: -100.0 <= x <= 100.0
)

_check_c_zero_air_pressure = Criterion(
    "cZeroAirPressure", lambda x: 300.0 <= x / 10 <= 1500.0
)

_check_c_zero_air_humidity = Criterion(
    "cZeroAirHumidity", lambda x: 0.0 <= x <= 100.0
)

_check_c_zero_w_pitch = Criterion(
    "cZeroWPitch", lambda x: -90.0 <= x <= 90
)

_check_c_zero_p_temperature = Criterion(
    "cZeroPTemperature", lambda x: -100.0 <= x <= 100.0
)

_check_c_zero_b_diameter = Criterion(
    "bDiameter", lambda x: 0.001 <= x / 1000 <= 50.0
)

_check_c_zero_b_weight = Criterion(
    "bWeight", lambda x: 1.0 <= x / 10 <= 6553.5
)

_check_c_zero_b_length = Criterion(
    "bLength", lambda x: 0.01 <= x / 1000 <= 200.0
)

_check_bc_type = Criterion(
    "bcType", lambda x: x in ['G7', 'G1', 'CUSTOM']
)

_check_distance = Criterion(
    "distance", lambda x: 1.0 <= x / 100 <= 3000.0
)


if __name__ == '__main__':
    v = Validator()
    # with open("bc_broken.a7p", "rb") as fp:
    with open("bc_ok.a7p", "rb") as fp:
        payload = A7PFile.load(fp, False)
        # print(payload.profile)
        v.validate(payload)
