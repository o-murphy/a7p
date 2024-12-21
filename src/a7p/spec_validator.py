from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Callable, Any, Tuple, Type

from google.protobuf.json_format import MessageToDict

from . import profedit_pb2
from .exceptions import SpecViolation, A7PSpecTypeError, A7PSpecValidationError

__all__ = ['SpecValidator', 'SpecCriterion']

from .protovalidate.validator import Validator

# def is_list_of_violations(violations: str | list[SpecViolation]):
#     """Check if a variable is a list of Violation objects."""
#     return isinstance(violations, list) and all(isinstance(item, SpecViolation) for item in violations)


# Define a custom type for the return value
SpecValidationResult = Tuple[bool, str | list[SpecViolation]]

# Define the type annotation for the callable
SpecValidatorFunction = Callable[[Any, Path, list], SpecValidationResult]
SpecFlexibleValidatorFunction = Callable[..., SpecValidationResult]


@dataclass
class SpecCriterion:
    path: Path
    validation_func: SpecFlexibleValidatorFunction

    def validate(self, data: any, path: Path | str, violations: list[SpecViolation]) -> SpecValidationResult:
        try:
            is_valid, reason = self.validation_func(data, path, violations)
            if not is_valid:
                violations.append(SpecViolation(path, data, str(reason)))
            return is_valid, reason
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
_check_twist_fir = lambda x, *args, **kwargs: assert_choice(x, ['RIGHT', 'LEFT'])

_check_c_zero_distance_idx = lambda x, *args, **kwargs: (0 <= x <= 200, "expected integer value in range [0, 200]")

_check_one_distance = lambda x, *args, **kwargs: assert_float_range(x, 1.0, 3000.0, 100)


def _check_distance_from(x, *args, **kwargs):
    if isinstance(x, (float, int)):
        return assert_float_range(x, 1.0, 3000.0, 100)
    if isinstance(x, str) and x == "VALUE":  # TODO: check special value
        return True, ""
    return False, "unexpected value or value type"


# switches spec checks
def _check_cidx(idx: int, *args, **kwargs) -> SpecValidationResult:
    if idx == 255:
        return True, "uses special 'unused' value '255'"  # TODO: 255 uses ad default ?
    return assert_int_range(idx, 0, 200)


_check_reticle_idx = lambda x, *args, **kwargs: assert_int_range(x, 0, 255)
_check_zoom = lambda x, *args, **kwargs: assert_int_range(x, 0, 4)


def _check_switches(switches: list, path: Path, violations: list[SpecViolation], *args, **kwargs):
    criterion = SpecCriterion(
        path,
        lambda x, *args, **kwargs: (x >= 4, f"expected minimum 4 items but got {x}")
    )

    criterion.validate(len(switches), path, violations)

    v = SpecValidator()
    v.register("cIdx", _check_cidx)
    v.register("reticleIdx", _check_reticle_idx)
    v.register("zoom", _check_zoom)
    v.register("distanceFrom", _check_distance_from)

    v.validate(switches, path, violations)

    return True, "No reasons"


_check_bc_type = lambda x, *args, **kwargs: assert_choice(x, ['G7', 'G1', 'CUSTOM'])

_check_bc_value = lambda x, *args, **kwargs: assert_float_range(x, 0.0, 10.0, 10000)
_check_cd_value = lambda x, *args, **kwargs: assert_float_range(x, 0.0, 10.0, 10000)
_check_ma_value = lambda x, *args, **kwargs: assert_float_range(x, 0.0, 10.0, 10000)
_check_mv_value = lambda x, *args, **kwargs: assert_float_range(x, 0.0, 3000.0, 10)


@assert_spec_type(tuple, list)
def assert_items_count(items, min_count, max_count):
    items_len = len(items)
    if items_len < min_count:
        return False, f"expected minimum {min_count} item(s) but got {items_len}"
    if items_len > max_count:
        return False, f"expected maximum {max_count} item(s) but got {items_len}"
    return True, ""


def _check_coef_rows(profile: dict, path: Path, violations: list[SpecViolation], *args, **kwargs):
    bc_type = profile['bcType']
    bc_criterion = SpecCriterion(Path("bcType"), _check_bc_type)
    coef_rows_violations = []

    # Validate the boundary condition type
    is_valid, reason = bc_criterion.validate(bc_type, path, coef_rows_violations)

    if is_valid:

        v = SpecValidator()

        # Register validation rules based on bcType
        if bc_type in ['G7', 'G1']:
            v.register("coefRows", lambda x, *args, **kwargs: assert_items_count(x, 1, 5))
            v.register("bcCd", _check_bc_value)
            v.register("mv", _check_mv_value)
        elif bc_type == 'CUSTOM':
            v.register("coefRows", lambda x, *args, **kwargs: assert_items_count(x, 1, 200))
            v.register("bcCd", _check_cd_value)
            v.register("mv", _check_ma_value)
        else:
            coef_rows_violations.append(
                SpecViolation(
                    path / "coefRows",
                    "Validation skipped for coefRows",
                    f"Unsupported bcType '{bc_type}'"
                )
            )

        # Perform the validation
        v.validate(profile, path, coef_rows_violations)

    # Handle violations
    if len(coef_rows_violations) <= 12:
        violations.extend(coef_rows_violations)
    else:
        violations.append(SpecViolation(
            path / "coefRows",
            f"Too many errors in {path / 'coefRows'}",
            "More than 12 errors found, listing all is omitted"
        ))

    return True, ""


def _check_distances(profile, path: Path, violations, *args, **kwargs):
    distances_violations = []

    idx = profile["cZeroDistanceIdx"]
    distances = profile["distances"]

    SpecCriterion(
        path / "cZeroDistanceIdx",
        _check_c_zero_distance_idx
    ).validate(
        idx,
        path / "cZeroDistanceIdx",
        distances_violations
    )

    is_valid, reason = _check_dependency_distances(idx, distances)
    if not is_valid:
        distances_violations.append(SpecViolation("Distances", "Distance dependency error", reason))

    SpecCriterion(
        path / "distances",
        lambda x, *args, **kwargs: assert_items_count(x, 1, 200)
    ).validate(distances, path / "distances", distances_violations)

    criterion = SpecCriterion(
        path / "[:]",
        _check_one_distance
    )

    for i, d in enumerate(distances):
        criterion.validate(d, path / 'distances' / f"[{i}]", distances_violations)

    # Handle violations
    if len(distances_violations) <= 11:
        violations.extend(distances_violations)
    else:
        violations.append(SpecViolation(
            path / "distances",
            f"Too many errors in {path / 'distances'}",
            "More than 10 errors found, listing all is omitted"
        ))

    return True, ""


def _check_dependency_distances(zero_distance_index: int, distances: list[int]):
    return 0 <= zero_distance_index < len(distances), "zero distance index > len(distances)"


def _check_profile(profile: dict, path: Path, violations: list[SpecViolation], *args, **kwargs):
    v = SpecValidator()
    v.register("~/profile/switches", _check_switches)

    v.validate(profile, path, violations)

    _check_distances(profile, path, violations, *args, **kwargs)
    _check_coef_rows(profile, path, violations, *args, **kwargs)

    return True, "Found problems in 'profile' section"


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
    "twistDir": _check_twist_fir,

    "~/profile": _check_profile
}


class _DefaultSpecValidator(SpecValidator):
    def __init__(self):
        super().__init__()
        for key, func in validation_functions.items():
            self.register(key, func)


_default_validator = _DefaultSpecValidator()


def validate_spec(payload: profedit_pb2.Payload):
    data = MessageToDict(payload, including_default_value_fields=True)

    is_valid, violations = _default_validator.validate(data)
    if not is_valid:
        raise A7PSpecValidationError("Spec Validation Error", payload, violations)
