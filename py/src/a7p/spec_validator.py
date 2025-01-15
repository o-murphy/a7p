"""
This module provides functionality for validating a payload based on specific validation criteria.

It includes the following components:

1. **Default Validation Functions**:
   A set of default validation functions for various fields, such as profile name, cartridge name, and ballistic coefficients. These functions ensure that values in the payload meet specified constraints, such as being of the correct type, length, or within valid ranges.

2. **SpecValidator Class**:
   The `SpecValidator` class is responsible for managing the validation criteria. It allows registering validation functions for specific paths within the payload and provides a method to validate the entire payload based on these functions.

3. **_DefaultSpecValidator Class**:
   This subclass of `SpecValidator` automatically registers a predefined set of validation functions for the most common payload fields. It is used to simplify the validation process by providing out-of-the-box validation logic for a variety of fields.

4. **validate_spec Function**:
   The `validate_spec` function is the main entry point for validating a payload. It converts a protobuf message into a dictionary, then uses `_DefaultSpecValidator` to validate the data. If the data is invalid, an `A7PSpecValidationError` is raised, which includes details about the violations.

Key Features:
- **Flexible Validation**: The validation functions are designed to be flexible, allowing for different kinds of validation checks, such as length checks, range checks, and type checks.
- **Customizable**: While a set of default validation functions is provided, additional validation functions can be added as needed for custom use cases.
- **Error Handling**: In case of validation errors, detailed violation information is provided, making it easier to debug and fix issues with the payload data.

Usage Example:
    To validate a payload, simply call `validate_spec(payload)` where `payload` is a protobuf message.

    If validation fails, an `A7PSpecValidationError` will be raised, which contains the details of the validation violations.

Module Dependencies:
    - profedit_pb2: Protobuf definition for the payload structure.
    - A7PSpecValidationError: Custom exception raised on validation failure.

"""

from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Callable, Any, Tuple, Type, Dict, Optional, Union, List

import a7p
from . import profedit_pb2
from .exceptions import SpecViolation, A7PSpecTypeError, A7PSpecValidationError

# Define a custom type for the return value
SpecValidationResult = Tuple[bool, Union[str, List['SpecViolation']]]

# Define the type annotation for the callable
SpecValidatorFunction = Callable[[Any, Path, List[Any]], SpecValidationResult]
SpecFlexibleValidatorFunction = Callable[..., SpecValidationResult]


@dataclass
class SpecCriterion:
    """
    Represents a specification criterion for validation.

    Attributes:
        path (Path): The path to the data element being validated.
        validation_func (SpecFlexibleValidatorFunction): The validation function used to check the data.

    Methods:
        validate(data, path, violations): Validates the data against the validation function and tracks violations.
    """
    path: Path
    validation_func: SpecFlexibleValidatorFunction

    def validate(self, data: Any, path: Union[Path, str], violations: List['SpecViolation']) -> SpecValidationResult:
        """
        Validates the given data and records violations if any.

        Parameters:
            data (Any): The data to validate.
            path (Union[Path, str]): The path of the data element.
            violations (List[SpecViolation]): The list of violations to append to.

        Returns:
            SpecValidationResult: A tuple containing the validity status and the associated message or violation details.
        """
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


def assert_spec_type(*expected_types: Type) -> Callable[[SpecFlexibleValidatorFunction], SpecFlexibleValidatorFunction]:
    """
    Decorator to validate the type of the first argument of the decorated function.

    Parameters:
        expected_types (Type): Expected types for the first argument.

    Returns:
        Callable: A wrapper function that validates the type of the first argument.
    """
    if not all(isinstance(t, type) for t in expected_types):
        raise ValueError("all expected_types must be valid types.")

    def decorator(func: SpecFlexibleValidatorFunction) -> SpecFlexibleValidatorFunction:
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


# assertion methods section
@assert_spec_type(str)
def assert_shorter_le(string: str, max_len: int) -> SpecValidationResult:
    """
    Asserts that the length of a string is shorter than the specified maximum length.

    Parameters:
        string (str): The string to check.
        max_len (int): The maximum length of the string.

    Returns:
        SpecValidationResult: A tuple containing a boolean indicating whether the string is shorter than max_len,
                              and an error message if not.
    """
    return len(string) <= max_len, f"expected string shorter than {max_len} characters"


@assert_spec_type(float, int)
def assert_float_range(value: float, min_value: float, max_value: float, divisor: float = 1) -> SpecValidationResult:
    """
    Asserts that a value is within a specified range, optionally divided by a divisor.

    Parameters:
        value (float): The value to check.
        min_value (float): The minimum value.
        max_value (float): The maximum value.
        divisor (float, optional): The divisor to divide the value by, default is 1.

    Returns:
        SpecValidationResult: A tuple containing a boolean indicating whether the value is within the range,
                              and a message if not.
    """
    return (min_value <= value / divisor <= max_value,
            f"expected value in range [{(min_value * divisor):.1f}, {(max_value * divisor):.1f}]")


@assert_spec_type(int)
def assert_int_range(value: int, min_value: int, max_value: int) -> SpecValidationResult:
    """
    Asserts that an integer value is within a specified range.

    Parameters:
        value (int): The integer value to check.
        min_value (int): The minimum value.
        max_value (int): The maximum value.

    Returns:
        SpecValidationResult: A tuple containing a boolean indicating whether the value is within the range,
                              and a message if not.
    """
    return min_value <= value <= max_value, f"expected integer value in range [{min_value}, {max_value}]"


def assert_choice(value: Any, keys: List[Any]) -> SpecValidationResult:
    """
    Asserts that a value is one of the specified choices.

    Parameters:
        value (Any): The value to check.
        keys (List[Any]): A list of valid choices.

    Returns:
        SpecValidationResult: A tuple containing a boolean indicating whether the value is one of the choices,
                              and a message if not.
    """
    return value in keys, f"expected one of {keys}"


@assert_spec_type(tuple, list)
def assert_items_count(items: Union[tuple, list], min_count: int, max_count: int) -> SpecValidationResult:
    """
    Asserts that the number of items in a tuple or list is within a specified range.

    Parameters:
        items (Union[tuple, list]): The collection of items to check.
        min_count (int): The minimum number of items.
        max_count (int): The maximum number of items.

    Returns:
        SpecValidationResult: A tuple containing a boolean indicating whether the number of items is within the range,
                              and a message if not.
    """
    items_len = len(items)
    if items_len < min_count:
        return False, f"expected minimum {min_count} item(s) but got {items_len}"
    if items_len > max_count:
        return False, f"expected maximum {max_count} item(s) but got {items_len}"
    return True, ""


class SpecValidator:
    """
    A class responsible for validating data according to specified criteria.

    Attributes:
        criteria (Dict[str, SpecCriterion]): A dictionary mapping paths to their corresponding validation criteria.

    Methods:
        register(path: Union[str, Path], criteria: SpecFlexibleValidatorFunction):
            Registers a validation criterion for a specified path.

        unregister(key: str):
            Unregisters the validation criterion for a specified path.

        get_criteria(path: Path) -> Optional[SpecCriterion]:
            Retrieves the validation criterion for a specified path.

        validate(data: Any, path: Path = Path("~/"), violations: Optional[List[SpecViolation]] = None) -> Tuple[bool, List[SpecViolation]]:
            Validates the provided data according to the registered criteria and collects any violations.
    """

    def __init__(self):
        """
        Initializes the SpecValidator with an empty criteria dictionary and a default registration.
        """
        self.criteria: Dict[str, SpecCriterion] = {}
        # Register a default validation that always passes
        self.register("~", lambda x, *args, **kwargs: (True, ""))

    def register(self, path: Union[Path, str], criteria: SpecFlexibleValidatorFunction):
        """
        Registers a validation criterion for a given path.

        Parameters:
            path (Union[Path, str]): The path to register the criterion for.
            criteria (SpecFlexibleValidatorFunction): The validation function to associate with the path.

        Raises:
            KeyError: If the path already has an associated validation criterion.
        """
        if path in self.criteria:
            raise KeyError(f"Criterion for {path} already exists.")
        self.criteria[str(path)] = SpecCriterion(Path(path), criteria)

    def unregister(self, key: str):
        """
        Unregisters the validation criterion for a given path.

        Parameters:
            key (str): The path of the criterion to remove.
        """
        self.criteria.pop(key, None)

    def get_criteria(self, path: Path) -> Optional[SpecCriterion]:
        """
        Retrieves the validation criterion for a specified path.

        Parameters:
            path (Path): The path to retrieve the validation criterion for.

        Returns:
            Optional[SpecCriterion]: The validation criterion associated with the path, or None if not found.
        """
        key = path.name
        criterion = self.criteria.get(key, None)
        if criterion is None:
            criterion = self.criteria.get(path.as_posix())
        return criterion

    def validate(self, data: Any, path: Path = Path("~/"), violations: Optional[List[SpecViolation]] = None) -> Tuple[
        bool, List[SpecViolation]]:
        """
        Validates the given data recursively according to the registered validation criteria.

        Parameters:
            data (Any): The data to validate.
            path (Path, optional): The current path being validated (default is Path("~/")).
            violations (Optional[List[SpecViolation]], optional): A list to accumulate validation violations (default is None).

        Returns:
            Tuple[bool, List[SpecViolation]]: A tuple where the first element is a boolean indicating if validation passed
                                              and the second element is a list of violations (if any).
        """
        if violations is None:
            violations = []

        # If `data` is a dictionary, recursively validate its key-value pairs
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = path / key
                self.validate(value, current_path, violations)

        # If `data` is a list, recursively validate its elements
        elif isinstance(data, list):
            for i, item in enumerate(data):
                item_path = path / f"[{i}]"
                self.validate(item, item_path, violations)

        # Validate the data at the current path according to its criterion
        criterion = self.get_criteria(path)
        if isinstance(criterion, SpecCriterion):
            criterion.validate(data, path, violations)

        return len(violations) == 0, violations


# Default validation functions section
def _check_profile_name(x: str, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the profile name is shorter than 50 characters."""
    return assert_shorter_le(x, 50)


def _check_cartridge_name(x: str, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the cartridge name is shorter than 50 characters."""
    return assert_shorter_le(x, 50)


def _check_caliber(x: str, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the caliber name is shorter than 50 characters."""
    return assert_shorter_le(x, 50)


def _check_bullet_name(x: str, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the bullet name is shorter than 50 characters."""
    return assert_shorter_le(x, 50)


def _check_device_uuid(x: str, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the device UUID is shorter than 50 characters."""
    return assert_shorter_le(x, 50)


def _check_short_name_top(x: str, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the short name (top) is shorter than 8 characters."""
    return assert_shorter_le(x, 8)


def _check_short_name_bot(x: str, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the short name (bottom) is shorter than 8 characters."""
    return assert_shorter_le(x, 8)


def _check_user_note(x: str, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the user note is shorter than 1024 characters."""
    return assert_shorter_le(x, 1024)


def _check_zero_x(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero x value is in the range of [-200.0, 200.0] with a divisor of 1000."""
    return assert_float_range(x, -200.0, 200.0, 1000)


def _check_zero_y(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero y value is in the range of [-200.0, 200.0] with a divisor of 1000."""
    return assert_float_range(x, -200.0, 200.0, 1000)


def _check_sc_height(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the SC height is in the range of [-5000.0, 5000.0]."""
    return assert_float_range(x, -5000.0, 5000.0)


def _check_r_twist(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the right twist value is in the range of [0.0, 100.0] with a divisor of 100."""
    return assert_float_range(x, 0.0, 100.0, 100)


def _check_c_muzzle_velocity(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the muzzle velocity is in the range of [10.0, 3000.0] with a divisor of 10."""
    return assert_float_range(x, 10.0, 3000.0, 10)


def _check_c_zero_temperature(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero temperature is in the range of [-100.0, 100.0]."""
    return assert_float_range(x, -100.0, 100.0)


def _check_c_t_coeff(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the temperature coefficient is in the range of [0.0, 5.0] with a divisor of 1000."""
    return assert_float_range(x, 0.0, 5.0, 1000)


def _check_c_zero_air_temperature(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero air temperature is in the range of [-100.0, 100.0]."""
    return assert_float_range(x, -100.0, 100.0)


def _check_c_zero_air_pressure(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero air pressure is in the range of [300.0, 1500.0] with a divisor of 10."""
    return assert_float_range(x, 300.0, 1500.0, 10)


def _check_c_zero_air_humidity(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero air humidity is in the range of [0.0, 100.0]."""
    return assert_float_range(x, 0.0, 100.0)


def _check_c_zero_w_pitch(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero wind pitch is in the range of [-90.0, 90.0] with a divisor of 10."""
    return assert_float_range(x, -90.0, 90.0, 10)


def _check_c_zero_p_temperature(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero pressure temperature is in the range of [-100.0, 100.0]."""
    return assert_float_range(x, -100.0, 100.0)


def _check_b_diameter(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero ballistic diameter is in the range of [0.001, 50.0] with a divisor of 1000."""
    return assert_float_range(x, 0.001, 50.0, 1000)


def _check_b_weight(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero ballistic weight is in the range of [1.0, 6553.5] with a divisor of 10."""
    return assert_float_range(x, 1.0, 6553.5, 10)


def _check_b_length(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero ballistic length is in the range of [0.01, 200.0] with a divisor of 1000."""
    return assert_float_range(x, 0.01, 200.0, 1000)


def _check_twist_dir(x: str, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the twist direction is either 'RIGHT' or 'LEFT'."""
    return assert_choice(x, ['RIGHT', 'LEFT'])


# Validation functions for distances/c_zero_distance_idx section
def _check_c_zero_distance_idx(x: int, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zero distance index is in the range of [0, 200]."""
    return assert_int_range(x, 0, 200)


def _check_one_distance(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the one distance value is in the range of [1.0, 3000.0] with a divisor of 100."""
    return assert_float_range(x, 1.0, 3000.0, 100)


# Validation functions for switches section
def _check_distance_from(x: Union[float, int, str], *args: Any, **kwargs: Any) -> SpecValidationResult:
    """
    Validates that the distance value is within the range [1.0, 3000.0] (divisor of 100),
    or is a special value "VALUE".
    """
    if isinstance(x, (float, int)):
        return assert_float_range(x, 1.0, 3000.0, 100)
    if isinstance(x, str) and x.lower() in ["value", "index"]:  # TODO: check special value
        return True, ""
    return False, "unexpected value or value type"


def _check_c_idx(idx: int, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the index is either '255' (special value) or in the range of [0, 200]."""
    if idx == 255:
        return True, "uses special 'unused' value '255'"
    return assert_int_range(idx, 0, 200)


def _check_reticle_idx(x: int, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the reticle index is in the range of [0, 255]."""
    return assert_int_range(x, 0, 255)


def _check_zoom(x: int, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the zoom value is in the range of [0, 4]."""
    return assert_int_range(x, 0, 6)


def _check_switches(switches: List[dict], path: Path, violations: List[SpecViolation], *args: Any,
                    **kwargs: Any) -> SpecValidationResult:
    """
    Validates the switches list, ensuring it contains at least 4 items, and validates each switch
    based on specific criteria (c_idx, reticle_idx, zoom, distance_from).
    """
    criterion = SpecCriterion(
        path,
        lambda x, *args, **kwargs: (x >= 4, f"expected minimum 4 items but got {x}")
    )
    criterion.validate(len(switches), path, violations)

    v = SpecValidator()
    v.register("c_idx", _check_c_idx)
    v.register("reticle_idx", _check_reticle_idx)
    v.register("zoom", _check_zoom)
    v.register("distance_from", _check_distance_from)

    v.validate(switches, path, violations)

    return True, "No reasons"


# Validation functions for bc type and bc/cd/mv values section
def _check_bc_type(x: str, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the ballistic coefficient type is one of 'G7', 'G1', or 'CUSTOM'."""
    return assert_choice(x, ['G7', 'G1', 'CUSTOM'])


def _check_bc_value(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the ballistic coefficient value is in the range of [0.0, 10.0] with a divisor of 10000."""
    return assert_float_range(x, 0.0, 10.0, 10000)


def _check_cd_value(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the drag coefficient value is in the range of [0.0, 10.0] with a divisor of 10000."""
    return assert_float_range(x, 0.0, 10.0, 10000)


def _check_ma_value(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the Mach value is in the range of [0.0, 10.0] with a divisor of 10000."""
    return assert_float_range(x, 0.0, 10.0, 10000)


def _check_mv_value(x: float, *args: Any, **kwargs: Any) -> SpecValidationResult:
    """Validates that the muzzle velocity value is in the range of [0.0, 3000.0] with a divisor of 10."""
    return assert_float_range(x, 0.0, 3000.0, 10)


# Validation function for coef_rows
def _check_coef_rows(profile: dict, path: Path, violations: List[SpecViolation], *args: Any, **kwargs: Any) -> Tuple[
    bool, str]:
    """
    Validates the 'coef_rows' field in the profile based on its 'bc_type'.
    The validation checks the number of coefficient rows and validates 'bc_cd' and 'mv' values
    based on the 'bc_type' (G7, G1, or CUSTOM).

    Args:
        profile (dict): The profile containing the data to validate.
        path (Path): The path to the profile data for error reporting.
        violations (list): A list to store the violations found during validation.

    Returns:
        Tuple[bool, str]: A tuple where the first element indicates if validation passed,
                           and the second element is a reason or message.
    """
    bc_type = profile['bc_type']
    bc_criterion = SpecCriterion(Path("bc_type"), _check_bc_type)
    coef_rows_violations = []

    # Validate the boundary condition type
    is_valid, reason = bc_criterion.validate(bc_type, path, coef_rows_violations)

    if is_valid:
        v = SpecValidator()

        # Register validation rules based on bc_type
        if bc_type in ['G7', 'G1']:
            v.register("coef_rows", lambda x, *args, **kwargs: assert_items_count(x, 1, 5))
            v.register("bc_cd", _check_bc_value)
            v.register("mv", _check_mv_value)
        elif bc_type == 'CUSTOM':
            v.register("coef_rows", lambda x, *args, **kwargs: assert_items_count(x, 1, 200))
            v.register("bc_cd", _check_cd_value)
            v.register("mv", _check_ma_value)
        else:
            coef_rows_violations.append(
                SpecViolation(
                    path / "coef_rows",
                    "Validation skipped for coef_rows",
                    f"Unsupported bc_type '{bc_type}'"
                )
            )

        # Perform the validation
        v.validate(profile, path, coef_rows_violations)

    # Handle violations
    if len(coef_rows_violations) <= 12:
        violations.extend(coef_rows_violations)
    else:
        violations.append(SpecViolation(
            path / "coef_rows",
            f"Too many errors in {path / 'coef_rows'}",
            "More than 12 errors found, listing all is omitted"
        ))

    return True, ""


# Validation function for distances
def _check_distances(profile: dict, path: Path, violations: List[SpecViolation], *args: Any, **kwargs: Any) -> Tuple[
    bool, str]:
    """
    Validates the 'distances' field and the 'c_zero_distance_idx' field in the profile.
    Ensures the zero distance index is valid and the distances are within the expected range.

    Args:
        profile (dict): The profile containing the data to validate.
        path (Path): The path to the profile data for error reporting.
        violations (list): A list to store the violations found during validation.

    Returns:
        Tuple[bool, str]: A tuple where the first element indicates if validation passed,
                           and the second element is a reason or message.
    """
    distances_violations = []

    idx = profile["c_zero_distance_idx"]
    distances = profile["distances"]

    SpecCriterion(
        path / "c_zero_distance_idx",
        _check_c_zero_distance_idx
    ).validate(
        idx,
        path / "c_zero_distance_idx",
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
        path / "[:] ",
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


def _check_dependency_distances(zero_distance_index: int, distances: List[int]) -> Tuple[bool, str]:
    """
    Validates the dependency between 'c_zero_distance_idx' and the 'distances' list.

    Args:
        zero_distance_index (int): The index representing the zero distance.
        distances (List[int]): A list of distances.

    Returns:
        Tuple[bool, str]: A tuple indicating if the validation passed, and a reason message if failed.
    """
    return 0 <= zero_distance_index < len(distances), "zero distance index > len(distances)"


# Validation function for profile
def _check_profile(profile: dict, path: Path, violations: List[SpecViolation], *args: Any, **kwargs: Any) -> Tuple[
    bool, str]:
    """
    Validates the entire profile, including switches, distances, and coef_rows.

    Args:
        profile (dict): The profile containing the data to validate.
        path (Path): The path to the profile data for error reporting.
        violations (list): A list to store the violations found during validation.

    Returns:
        Tuple[bool, str]: A tuple indicating if validation passed, and a reason or message.
    """
    v = SpecValidator()
    v.register("~/profile/switches", _check_switches)

    v.validate(profile, path, violations)

    _check_distances(profile, path, violations, *args, **kwargs)
    _check_coef_rows(profile, path, violations, *args, **kwargs)

    return True, "Found problems in 'profile' section"


# Type alias for validation function
SpecValidationFunction = Callable[..., Tuple[bool, str]]

# Default validation functions dictionary
_default_validation_funcs: Dict[str, SpecValidationFunction] = {
    "profile_name": _check_profile_name,
    "cartridge_name": _check_cartridge_name,
    "caliber": _check_caliber,
    "bullet_name": _check_bullet_name,
    "device_uuid": _check_device_uuid,
    "short_name_top": _check_short_name_top,
    "short_name_bot": _check_short_name_bot,
    "user_note": _check_user_note,
    "zero_x": _check_zero_x,
    "zero_y": _check_zero_y,
    "sc_height": _check_sc_height,
    "r_twist": _check_r_twist,
    "c_muzzle_velocity": _check_c_muzzle_velocity,
    "c_zero_temperature": _check_c_zero_temperature,
    "c_t_coeff": _check_c_t_coeff,
    "c_zero_air_temperature": _check_c_zero_air_temperature,
    "c_zero_air_pressure": _check_c_zero_air_pressure,
    "c_zero_air_humidity": _check_c_zero_air_humidity,
    "c_zero_p_temperature": _check_c_zero_p_temperature,
    "c_zero_w_pitch": _check_c_zero_w_pitch,
    "b_length": _check_b_length,
    "b_weight": _check_b_weight,
    "b_diameter": _check_b_diameter,
    "twist_dir": _check_twist_dir,

    "~/profile": _check_profile
}


class _DefaultSpecValidator(SpecValidator):
    def __init__(self):
        super().__init__()
        # Register all default validation functions
        for key, func in _default_validation_funcs.items():
            self.register(key, func)


_default_validator = _DefaultSpecValidator()


def validate_spec(payload: profedit_pb2.Payload) -> None:
    """
    Validates a given payload using the default validator.

    Args:
        payload (profedit_pb2.Payload): The payload to validate.

    Raises:
        A7PSpecValidationError: If validation fails, raises an exception with details.
    """
    # Convert protobuf message to dictionary, including default values
    data = a7p.to_dict(payload)

    # Perform validation
    is_valid, violations = _default_validator.validate(data)

    # Raise an error if validation fails
    if not is_valid:
        raise A7PSpecValidationError("Spec Validation Error", payload, violations)


__all__ = (
    'SpecValidator',
    'SpecCriterion',
    'validate_spec',
    'assert_spec_type',
    'assert_items_count',
    'assert_shorter_le',
    'assert_float_range',
    'assert_int_range',
    'assert_choice',
    'SpecValidationResult',
    'SpecValidationFunction',
    'SpecFlexibleValidatorFunction',
)
