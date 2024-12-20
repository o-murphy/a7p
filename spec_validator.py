import pathlib
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Callable, Any, Tuple, Type

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
        path = f"Path:    :{self.path}" if isinstance(self.path, Path) else self.path
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


class A7PSpecValidationError(A7PDataError):
    def __init__(self, violations: list[SpecViolation]):
        self.violations = violations


class A7PSpecTypeError(A7PDataError):
    def __init__(self, expected_types: tuple[Type, ...] = None, actual_type: Type = None):
        self.expected_types = expected_types or "UNKNOWN"
        self.actual_type = actual_type or "UNKNOWN"
        self.message = f"expected value to be one of types: {[t.__name__ for t in expected_types]}, "
        f"but got {actual_type.__name__} instead."
        super().__init__(self.message, self.expected_types, self.actual_type)


@dataclass
class SpecCriterion:
    path: Path
    validation_func: SpecFlexibleValidatorFunction

    def validate(self, data: any, path: pathlib.Path, violations: list[SpecViolation]) -> SpecValidationResult:
        try:
            is_valid, reason = self.validation_func(data, path, violations)
            if not is_valid:
                violations.append(SpecViolation(path, data, str(reason)))
        except TypeError as err:
            violations.append(SpecViolation(path, data, f"Type error: {str(err)}"))
            return False, f"Type error: {str(err)}"
        except A7PSpecTypeError as err:
            violations.append(SpecViolation(path, data, f"Type error: {err.message}"))
            return False, f"Type error: {err.message}"


def assert_spec_type(*expected_types: Type):
    if not all(isinstance(t, type) for t in expected_types):
        raise ValueError("all expected_types must be valid types.")

    def decorator(func: SpecFlexibleValidatorFunction):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if args:
                first_arg = args[0]
                if not isinstance(first_arg, tuple(expected_types)):
                    raise A7PSpecTypeError(
                        tuple(expected_types),
                        type(first_arg)
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator


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
            criterion.validate(data, path, violations)
        return len(violations) == 0, violations


@assert_spec_type(str)
def assert_shorter(string: str, max_len: int):
    return len(string) < max_len, f"expected string shorter than {max_len} characters"


@assert_spec_type(float, int)
def assert_float_range(value: float, min_value: float, max_value: float, divisor: float = 1):
    return (min_value <= value / divisor <= max_value,
            f"expected value in range [{(min_value * divisor):.1f}, {(max_value * divisor):.1f}]")


@assert_spec_type(int)
def assert_int_range(value: int, min_value: int, max_value: int):
    return min_value <= value <= max_value, f"expected integer value in range [{min_value}, {max_value}]"


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
_check_zero_x = lambda x, *args, **kwargs: assert_float_range(x, -200.0, 200.0, 1000)
_check_zero_y = lambda x, *args, **kwargs: assert_float_range(x, -200.0, 200.0, 1000)
_check_sc_height = lambda x, *args, **kwargs: assert_float_range(x, -5000.0, 5000.0)
_check_r_twist = lambda x, *args, **kwargs: assert_float_range(x, 0.0, 100.0, 100)
_check_c_muzzle_velocity = lambda x, *args, **kwargs: assert_float_range(x, 10.0, 3000.0, 10)
_check_c_zero_temperature = lambda x, *args, **kwargs: assert_float_range(x, -100.0, 100.0)
_check_c_t_coeff = lambda x, *args, **kwargs: assert_float_range(x, 0.0, 5.0, 1000)
_check_c_zero_air_temperature = lambda x, *args, **kwargs: assert_float_range(x, -100.0, 100.0)
_check_c_zero_air_pressure = lambda x, *args, **kwargs: assert_float_range(x, 300.0, 1500.0, 10)
_check_c_zero_air_humidity = lambda x, *args, **kwargs: assert_float_range(x, 0.0, 100.0)
_check_c_zero_w_pitch = lambda x, *args, **kwargs: assert_float_range(x, -90.0, 90.0, 10)
_check_c_zero_p_temperature = lambda x, *args, **kwargs: assert_float_range(x, -100.0, 100.0)
_check_c_zero_b_diameter = lambda x, *args, **kwargs: assert_float_range(x, 0.001, 50.0, 1000)
_check_c_zero_b_weight = lambda x, *args, **kwargs: assert_float_range(x, 1.0, 6553.5, 10)
_check_c_zero_b_length = lambda x, *args, **kwargs: assert_float_range(x, 0.01, 200.0, 1000)
_check_bc_type = lambda x, *args, **kwargs: assert_choice(x, ['G7', 'G1', 'CUSTOM'])
_check_twist_fir = lambda x, *args, **kwargs: assert_choice(x, ['RIGHT', 'LEFT'])

_check_c_zero_distance_idx = lambda x, *args, **kwargs: (0 <= x <= 200, "expected integer value in range [0, 200]")

_check_one_distance = lambda x, *args, **kwargs: assert_float_range(x, 1.0, 3000.0, 100)


# switches spec checks
def _check_cidx(idx: int, *args, **kwargs) -> SpecValidationResult:
    if idx == 255:
        return False, "uses special 'unused value '255'"
    return assert_int_range(idx, 0, 200)


_check_reticle_idx = lambda x, *args, **kwargs: assert_int_range(x, 0, 255)
_check_zoom = lambda x, *args, **kwargs: assert_int_range(x, 0, 4)


def _check_switches(switches: list, path: Path, violations: list[SpecViolation], *args, **kwargs):
    switches.pop(0)
    switchesLen = len(switches)
    if switchesLen < 4:
        violations.append(SpecViolation(
            path=path,
            value=f"{switchesLen} < 4",
            reason=f"expected minimum 4 items but got {switchesLen}",
        ))

    v = SpecValidator()
    v.register("cIdx", _check_cidx)
    v.register("reticleIdx", _check_reticle_idx)
    v.register("zoom", _check_zoom)
    v.register("distanceFrom", _check_one_distance)

    v.validate(switches, path, violations)

    return True, "NOT IMPLEMENTED"


def _check_coef_rows(profile: dict, path: Path, violations: list[SpecViolation], *args, **kwargs):
    # TODO: coefRows / bc / custom
    return True, "NOT IMPLEMENTED"


def _check_distances(distances: list[int], path: Path, violations, *args, **kwargs):
    reasons = []
    invalid_distances = []
    if len(distances) < 1:
        reasons.append(f"expected minimum 1 item(s) but got {len(distances)}")
    elif len(distances) > 200:
        reasons.append(f"expected maximum 200 item(s) but got {len(distances)}")

    for i, d in enumerate(distances):
        d_path = path / f"[{i}]"
        is_valid_d, reason = _check_one_distance(d, d_path, violations)
        if not is_valid_d:
            invalid_distances.append(d)
    if len(invalid_distances) > 0:
        reasons.append(f"Invalid distances: {invalid_distances}")
    print(reasons)
    return len(reasons) == 0, f"[ {', '.join(reasons)} ]"


def _check_dependency_distances(zero_distance_index: int, distances: list[int]):
    return 0 <= zero_distance_index < len(distances), "zero distance index > len(distances)"


def _check_profile(profile: dict, path: Path, violations: list[SpecViolation], *args, **kwargs):
    v = SpecValidator()
    v.register("~/profile/distances", _check_distances)
    v.register("~/profile/cZeroDistanceIdx", _check_c_zero_distance_idx)

    v.register("~/profile/switches", _check_switches)
    # TODO: coefRows / bc / custom
    # v.register("~/profile/coefRows", _check_coef_rows)

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
