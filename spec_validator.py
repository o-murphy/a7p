from pathlib import Path
from dataclasses import dataclass
from typing import Callable, Any, Tuple

from a7p.a7p import profedit_pb2, A7PFile, A7PDataError
from a7p.logger import logger

__all__ = ['SpecValidator', 'SpecCriterion', 'A7PSpecValidationError']


@dataclass
class SpecViolation:
    path: Path | str
    value: any
    reason: str

    def format(self) -> str:
        is_stringer = isinstance(self.value, (str, int, float, bool))
        path = f"Path: {self.path}" if isinstance(self.path, Path) else self.path
        value = f"{self.value if is_stringer else '<object>'}"
        return f"Violation:\n\t{path}:\t{value}\n\tReason:\t{self.reason}"


def is_list_of_violations(violations: str | list[SpecViolation]):
    """Check if a variable is a list of Violation objects."""
    return isinstance(violations, list) and all(isinstance(item, SpecViolation) for item in violations)


# Define a custom type for the return value
SpecValidationResult = Tuple[bool, str | list[SpecViolation]]

# Define the type annotation for the callable
SpecValidatorFunction = Callable[[Any, Path, list], SpecValidationResult]
SpecFlexibleValidatorFunction = Callable[..., SpecValidationResult]


@dataclass
class SpecCriterion:
    path: Path
    validate: SpecFlexibleValidatorFunction


class A7PSpecValidationError(A7PDataError):
    def __init__(self, violations: list[SpecViolation]):
        self.violations = violations


class SpecValidator:
    def __init__(self):
        self.criteria = {}

        self.register("~", lambda x, *args, **kwargs: (True, ""))

    def register(self, path: Path | str, criteria: SpecFlexibleValidatorFunction):
        if path in self.criteria:
            raise KeyError(f"criterion for {path} already exists")
        self.criteria[path] = SpecCriterion(Path(path), criteria)

    def unregister(self, key: str):
        self.criteria.pop(key, None)

    def get_criteria(self, path: Path) -> SpecCriterion:
        key = path.name
        criterion = self.criteria.get(key, None)
        if criterion is None:
            criterion = self.criteria.get(path.as_posix())
        # for key, value in self.criteria.items():
        #     if key
        # if criterion is None:
        #     print(
        #         f"NoValidatorsRegistered\t{path.as_posix()}")
        return criterion

    def validate(self, data: any, path: Path = Path("~/"),
                 violations: list[SpecViolation] = None) -> (bool, list[SpecViolation]):

        if violations is None:
            violations = []
        if isinstance(data, dict):

            # If `data` is a dictionary, iterate over its key-value pairs
            for key, value in data.items():
                current_path = path / key
                self.validate(value, current_path, violations)

        elif isinstance(data, list):

            # If `data` is a list, iterate over its elements
            for i, item in enumerate(data):
                item_path = path / f"[{i}]"
                self.validate(item, item_path, violations)

        criterion = self.get_criteria(path)
        if isinstance(criterion, SpecCriterion):
            is_valid, reason = criterion.validate(data, path, violations)
            if not is_valid:
                violations.append(SpecViolation(path, data, str(reason)))
                # raise A7PValidationError(f"{path.as_posix()} has not valid value: {data}. Reason: {reason}")
        return len(violations) == 0, violations


def assert_shorter(string: str, max_len: int):
    return len(string) < max_len, f"expected string shorter than {max_len} characters"

def assert_range(value: float, min_value: float, max_value: float, divisor: float = 1):
    return -200.0 <= value / divisor <= 200.0, f"expected value in range [{min_value*divisor:.1f}, {max_value*divisor:.1f}]"

def assert_choice(value, keys: list):
    return value in keys, f"expected one of {keys}"

_check_profile_name = lambda x, *args, **kwargs: assert_shorter(x, 50)
_check_cartridge_name = lambda x, *args, **kwargs: assert_shorter(x, 50)
_check_caliber = lambda x, *args, **kwargs: assert_shorter(x, 50)
_check_bullet_name = lambda x, *args, **kwargs: assert_shorter(x, 50)
_check_device_uuid = lambda x, *args, **kwargs: assert_shorter(x, 50)
_check_short_name_top = lambda x, *args, **kwargs: assert_shorter(x, 8)
_check_short_name_bot = lambda x, *args, **kwargs: assert_shorter(x, 8)
_check_user_note = lambda x, *args, **kwargs: assert_shorter(x, 1024)
_check_zero_x = lambda x, *args, **kwargs: assert_range(x, -200.0, 200.0, 1000)
_check_zero_y = lambda x, *args, **kwargs: assert_range(x, -200.0, 200.0, 1000)
_check_sc_height = lambda x, *args, **kwargs: assert_range(x, -5000.0, 5000.0, 1000)
_check_r_twist = lambda x, *args, **kwargs: assert_range(x, 0.0, 100.0, 10)
_check_c_muzzle_velocity = lambda x, *args, **kwargs: assert_range(x, 10.0, 3000.0, 10)
_check_c_zero_temperature = lambda x, *args, **kwargs: assert_range(x, -100.0, 100.0)
_check_c_t_coeff = lambda x, *args, **kwargs: assert_range(x, 0.0, 5.0, 1000)
_check_c_zero_air_temperature = lambda x, *args, **kwargs: assert_range(x, -100.0, 100.0)
_check_c_zero_air_pressure = lambda x, *args, **kwargs: assert_range(x, 300.0, 1500.0, 10)
_check_c_zero_air_humidity = lambda x, *args, **kwargs: assert_range(x, 0.0, 100.0)
_check_c_zero_w_pitch = lambda x, *args, **kwargs: assert_range(x, -90.0, 90.0)
_check_c_zero_p_temperature = lambda x, *args, **kwargs: assert_range(x, -100.0, 100.0)
_check_c_zero_b_diameter = lambda x, *args, **kwargs: assert_range(x, 0.001, 50.0, 1000)
_check_c_zero_b_weight = lambda x, *args, **kwargs: assert_range(x, 1.0, 6553.5, 10)
_check_c_zero_b_length = lambda x, *args, **kwargs: assert_range(x, 0.01, 200.0, 1000)
_check_bc_type = lambda x, *args, **kwargs: assert_choice(x, ['G7', 'G1', 'CUSTOM'])
_check_twist_fir = lambda x, *args, **kwargs: assert_choice(x, ['RIGHT', 'LEFT'])

_check_c_zero_distance_idx = lambda x, *args, **kwargs: (0 <= x <= 200, "expected integer value in range [0, 200]")

_check_one_distance = lambda x, *args, **kwargs: assert_range(x, 1.0, 3000.0, 100)

def _check_switches(profile: list, path: Path, *args, **kwargs):
    return True, "NOT IMPLEMENTED"


def _check_coef_rows(profile: dict, path: Path, *args, **kwargs):
    return True, "NOT IMPLEMENTED"


def _check_distances(distances: list[int], path: Path, *args, **kwargs):
    reasons = []
    invalid_distances = []
    if not (0 < len(distances) < 200):
        reasons.append("distances count have been between 0 and 200 values")
    for i, d in enumerate(distances):
        path / f"[{i}]"
        is_valid_d, reason = _check_one_distance
        if not is_valid_d:
            invalid_distances.append(d)
    if len(invalid_distances) > 0:
        reasons.append(f"Invalid distances: {invalid_distances}")
    return len(reasons) == 0, f"[ {', '.join(reasons)} ]"


def _check_dependency_distances(zero_distance_index: int, distances: list[int]):
    return 0 <= zero_distance_index < len(distances), "zero distance index > len(distances)"


def _check_profile(profile: dict, path: Path, violations: list[SpecViolation], *args, **kwargs):
    v = SpecValidator()
    v.register("~/profile/distances", _check_distances)
    v.register("~/profile/cZeroDistanceIdx", _check_c_zero_distance_idx)

    v.register("~/profile/switches", _check_switches)
    v.register("~/profile/coefRows", _check_coef_rows)

    v.validate(profile, path, violations)

    is_valid, reason = _check_dependency_distances(profile["cZeroDistanceIdx"], profile["distances"])
    if not is_valid:
        violations.append(SpecViolation("Distances", "Distance dependency error", reason))

    return is_valid, "Found problems in 'profile' section"


_default_validation_funcs = validation_functions = {
    "profileName": _check_profile_name,
    "cartridgeName": _check_cartridge_name,
    "caliber": _check_caliber,
    "bulletName": _check_bullet_name,
    "deviceUuid": _check_device_uuid,
    "shortNameTop": _check_short_name_top,
    "shortNameBot": _check_short_name_bot,
    "userNote": _check_user_note,
    "zeroX": _check_zero_x,
    "zeroY": _check_zero_y,
    "scHeight": _check_sc_height,
    "rTwist": _check_r_twist,
    "cMuzzleVelocity": _check_c_muzzle_velocity,
    "cZeroTemperature": _check_c_zero_temperature,
    "cTCoeff": _check_c_t_coeff,
    "cZeroAirTemperature": _check_c_zero_air_temperature,
    "cZeroAirPressure": _check_c_zero_air_pressure,
    "cZeroAirHumidity": _check_c_zero_air_humidity,
    "cZeroPTemperature": _check_c_zero_p_temperature,
    "cZeroWPitch": _check_c_zero_w_pitch,
    "bLength": _check_c_zero_b_length,
    "bWeight": _check_c_zero_b_weight,
    "bDiameter": _check_c_zero_b_diameter,
    "bcType": _check_bc_type,
    "twistDir": _check_twist_fir,

    "~/profile": _check_profile
}


class _DefaultValidator(SpecValidator):
    def __init__(self):
        super().__init__()
        for key, func in validation_functions.items():
            self.register(key, func)


_default_validator = _DefaultValidator()


def validate(payload: profedit_pb2.Payload):
    data = A7PFile.to_dict(payload)

    is_valid, violations = _default_validator.validate(data)
    if not is_valid:
        raise A7PSpecValidationError(violations)


if __name__ == '__main__':

    with open("broken.a7p", "rb") as fp:
        payload = A7PFile.load(fp, False)
    try:
        validate(payload)
    except A7PSpecValidationError as e:
        for vio in e.violations:
            logger.warning(vio.format())
