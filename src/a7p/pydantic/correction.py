import math
from functools import wraps
from typing import Callable, Optional, Any

from annotated_types import Interval, MultipleOf
from pydantic import StringConstraints
from pydantic_core.core_schema import FieldValidationInfo
from typing_extensions import get_args
from a7p.logger import logger

from a7p.recover import RecoverResult


def pre_validate_interval(value: Any, interval: Optional[Interval]) -> None:
    """
    Validates that a value is within the specified interval.

    Args:
        value (Any): The value to validate.
        interval (Optional[Interval]): The interval constraints to check against.

    Raises:
        ValueError: If the value is outside the bounds specified in the interval.
    """
    if interval is None:
        return
    if interval.ge is not None and value < interval.ge:
        raise ValueError(f"value must be greater than or equal to %s" % interval.ge)
    if interval.le is not None and value > interval.le:
        raise ValueError(f"value must be less than or equal to %s" % interval.le)
    if interval.gt is not None and value <= interval.gt:
        raise ValueError(f"value must be greater than %s" % interval.gt)
    if interval.lt is not None and value >= interval.lt:
        raise ValueError(f"value must be less than %s" % interval.lt)


def pre_validate_multiple_of(value: Any, multiple_of: Optional[MultipleOf]) -> None:
    """
    Validates that a value is a multiple of a specified number.

    Args:
        value (Any): The value to validate.
        multiple_of (Optional[MultipleOf]): The multiple constraint.

    Raises:
        ValueError: If the value is not a multiple of the specified number.
    """
    if multiple_of is not None and multiple_of.multiple_of is not None:
        if value % multiple_of.multiple_of != 0:
            raise ValueError(f"value must be a multiple of %s" % multiple_of.multiple_of)


def pre_validate_conint(
        type_: type, strict: bool, interval: Optional[Interval], multiple_of: Optional[MultipleOf]
) -> Callable[[Any], Any]:
    """
    Returns a validation function for integer types with specified constraints.

    Args:
        type_ (type): The type to check against.
        strict (bool): Whether strict type checking is enabled.
        interval (Optional[Interval]): The interval constraints to check.
        multiple_of (Optional[MultipleOf]): The multiple of constraint to check.

    Returns:
        Callable[[Any], Any]: A function that validates the value.
    """

    def validate(value: Any) -> Any:
        if strict and not isinstance(value, type_):
            raise TypeError(f"value must be of type %s" % type_)
        value = type_(value)
        pre_validate_interval(value, interval)
        pre_validate_multiple_of(value, multiple_of)
        return value

    return validate


def pre_validate_confloat(
        type_: type, strict: bool, interval: Optional[Interval], multiple_of: Optional[MultipleOf], allow_inf_nan: bool
) -> Callable[[Any], Any]:
    """
    Returns a validation function for float types with specified constraints.

    Args:
        type_ (type): The type to check against.
        strict (bool): Whether strict type checking is enabled.
        interval (Optional[Interval]): The interval constraints to check.
        multiple_of (Optional[MultipleOf]): The multiple of constraint to check.
        allow_inf_nan (bool): Whether to allow NaN and Infinity values.

    Returns:
        Callable[[Any], Any]: A function that validates the value.
    """

    def validate(value: Any) -> Any:
        if strict and not isinstance(value, type_):
            raise TypeError(f"value must be of type %s" % type_)

        value = type_(value)
        pre_validate_interval(value, interval)
        pre_validate_multiple_of(value, multiple_of)

        if allow_inf_nan:
            if math.isnan(value):
                raise ValueError("value is NaN")
            elif math.isinf(value):
                raise ValueError("Value is positive infinity" if value > 0 else "Value is negative infinity")

        return value

    return validate


def pre_validate_constr(type_: type, str_constraints: Optional[StringConstraints]) -> Callable[[Any], Any]:
    """
    Handles validation for string types with additional constraints.

    Args:
        type_ (type): The type to check against (expected to be str).
        str_constraints (Any): The string constraints to check (e.g., max length, pattern).

    """

    def validate(value: Any) -> Any:
        if str_constraints is not None:
            if str_constraints.strict and not isinstance(value, type_):
                raise TypeError(f"Input should be a valid string")
            else:
                value: str = type_(value)

            if str_constraints.min_length is not None and len(value) < str_constraints.min_length:
                raise ValueError(f"Value error, String have been longer than %s" % str_constraints.min_length)
            if str_constraints.max_length is not None and len(value) > str_constraints.max_length:
                raise ValueError(f"Value error, String have been shorter than %s" % str_constraints.max_length)

            return value
        return type_(value)

    return validate


def retrieve_confield_validator(cls: type, field_name: str) -> Callable[[Any], Any]:
    """
    Retrieves the field validator for a given field in a class.

    Args:
        cls (type): The class containing the field.
        field_name (str): The name of the field for which to retrieve the validator.

    Returns:
        Callable[[Any], Any]: The validator function for the field.

    Raises:
        AttributeError: If the field is not found in the class.
        TypeError: If the field's type cannot be validated.
    """
    field = cls.__annotations__.get(field_name, None)
    if field is None:
        raise AttributeError(f"Field '%s' is not defined" % field_name)

    args = get_args(field)

    try:
        type_ = args[0]
    except IndexError:
        raise TypeError(f"typing.Annotated should have at least one item")

    try:
        if type_ is int:
            return pre_validate_conint(*args)
        elif type_ is float:
            return pre_validate_confloat(*args)
        elif type_ is str:
            return pre_validate_constr(*args)
        else:
            raise TypeError(f"Can't validate field type '%s'" % type_)
    except TypeError as err:
        raise TypeError(f"Field '%s' is not valid confield" % field_name) from err


def trigger_confield_validation(cls, value, info: FieldValidationInfo):
    validate = retrieve_confield_validator(cls, info.field_name)
    if callable(validate):
        value = validate(value)
    return value

def on_restore(handler: Callable[[type, Any, FieldValidationInfo, Exception], Any]) -> \
        Callable[[Callable], Callable]:
    """
    A decorator that applies a correction function if validation fails.

    Args:
        handler (Optional[Callable]): The correction function to use when validation fails.

    Returns:
        Callable[[Callable], Callable]: The decorator that wraps the validation function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(cls: type, value: Any, info: FieldValidationInfo) -> Any:
            ctx = info.context or {}
            if ctx.get("restore") and handler is not None:
                try:
                    return func(cls, value, info)
                except (TypeError, ValueError) as err:
                    logger.debug(f"Validation of field '{info.field_name}' failed with error: {err}")

                    if 'restored' not in info.context:
                        info.context['restored'] = {}

                    if callable(handler):
                        logger.debug("Invoking handler")
                        result = handler(cls, value, info, err)
                        info.context['restored'].append(RecoverResult(
                            recovered=True,
                            path=info.field_name,
                            old_value=value,
                            new_value=result
                        ))
                        return result
                    return value

            return func(cls, value, info)

        return wrapper

    return decorator


def example_handler(cls: type, value: Any, info: FieldValidationInfo, err: Exception) -> Any:
    """
    A sample handler that modifies the value in case of validation errors.

    Args:
        cls (type): The class containing the field.
        value (Any): The value to correct.
        info (FieldValidationInfo): The field validation info.
        err (Exception): The exception that occurred during validation.

    Returns:
        Any: The corrected value.
    """
    logger.debug(f"Handler modifying value: {value} due to error: {err}")
    if 'restored' not in info.context:
        info.context['restored'] = {}
    info.context['restored'][info.field_name] = err
    return 0
