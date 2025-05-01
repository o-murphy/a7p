from typing_extensions import TypedDict

from yup.validation_error import ErrorMessage

__all__ = (
    'locale',
    'set_locale'
)


class Locale(TypedDict):
    type: ErrorMessage
    min: ErrorMessage
    max: ErrorMessage
    length: ErrorMessage
    required: ErrorMessage
    not_nullable: ErrorMessage
    test: ErrorMessage
    matches: ErrorMessage
    email: ErrorMessage
    url: ErrorMessage
    uuid: ErrorMessage
    lowercase: ErrorMessage
    uppercase: ErrorMessage
    le: ErrorMessage
    ge: ErrorMessage
    lt: ErrorMessage
    gt: ErrorMessage
    integer: ErrorMessage
    multiple_of: ErrorMessage
    positive: ErrorMessage
    negative: ErrorMessage
    array_of: ErrorMessage
    shape: ErrorMessage
    shape_values: ErrorMessage
    one_of: ErrorMessage


locale: Locale = {
    "type": lambda args: "Value is not of type %r, got %r" % args,
    "min": lambda args: "Min length must be %r" % args,
    "max": lambda args: "Max length must be %r" % args,
    "length": lambda args: "Length must be %r" % args,
    "uppercase": "Value must be an uppercase string",
    "lowercase": "Value must be a lowercase string",
    "required": "Field is required",
    "not_nullable": "Value can't be null",
    "test": "Test failed",
    # 'matches':
    "email": "Value must be a valid email",
    "url": "Value must be a valid URL",
    "uuid": "Value must be a valid UUID",
    "le": lambda args: "Value must be less or equal to %r" % args,
    "ge": lambda args: "Value must be greater or equal to %r" % args,
    "lt": lambda args: "Value must be less than %r" % args,
    "gt": lambda args: "Value must be greater than %r" % args,
    "positive": "Value must be positive, a.g. > 0",
    "negative": "Value must be positive, a.g. < 0",
    "integer": "Value must be valid 'int', got 'float'",
    "array_of": lambda args: "Schema must be a type of Schema, got %r" % args,
    "multiple_of": lambda args: "Value must be a multiple of %r" % args,
    "shape": "'shape' must be a type of 'Shape'",
    "shape_values": "all shape items must have a values of type of Schema",
    "one_of": lambda args: "Must be one of %r" % args
}


def set_locale(locale_: TypedDict) -> TypedDict:
    locale.update(locale_)
