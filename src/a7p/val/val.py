import re
from dataclasses import dataclass, field

from typing_extensions import Any, Callable, Union, Self, List, Literal, Dict

ErrorMessage = Union[str, Callable[[], Any]]


class ValidationError(ValueError):
    def __init__(self, message: ErrorMessage = "Validation error",
                 path: str = "", errors: List[Self] = None, *args) -> None:
        super().__init__(message, *args)
        self.path = re.sub(r"^\.", "", path)
        # self.message = f"`{self.path}`: {message}"
        self.message = message
        self.errors = errors or []

    def __str__(self):
        return f"`{self.path}`: {self.message}"


rUUID_pattern = re.compile(
    r"^(?:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}|00000000-0000-0000-0000-000000000000)$",
    re.IGNORECASE,
)

rEmail_pattern = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    re.IGNORECASE,
)

rUrl_pattern = re.compile(
    r"^((https?|ftp):)?\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!$&'()*+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)|\/|\?)*)?$",
    re.IGNORECASE,
)

TransformFunc = List[Callable[[Any], Any]]
ValidatorFunc = List[Callable[[Any], None]]


@dataclass
class Schema:
    _type: Any = field(init=False, default=Any)
    _transforms: TransformFunc = field(init=False, default_factory=list)
    _validators: ValidatorFunc = field(init=False, default_factory=list)
    _optional: bool = True

    @property
    def optional(self) -> bool:
        return self._optional

    def required(self, message: ErrorMessage = "required") -> Self:  # FIXME
        self._optional = False
        return self

    def validate(self, value: Any, path: str = ""):
        type_ = self._type
        if type_ is not Any and not isinstance(value, type_):
            raise ValidationError(f"Value `{repr(value)}` is not of type {type_}, got {type(value)}")

        try:
            for validator in self._validators:
                validator(value)
        except ValidationError as err:
            raise ValidationError(err.message, path)

@dataclass
class StringSchema(Schema):
    _type: Any = field(init=False, default=str)

    def length(self, limit: int, message: ErrorMessage = "length") -> Self:
        def _(x: str):
            if len(x) != limit:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def min(self, limit: int, message: ErrorMessage = "min") -> Self:
        def _(x: str):
            if len(x) < limit:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def max(self, limit: int, message: ErrorMessage = "max") -> Self:
        def _(x: str):
            if len(x) > limit:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    # def matches(self, regex: re.Pattern, message: ErrorMessage, exclude_empty: bool = False) -> Schema:
    #     def _(x: str):
    #         if not re.match(regex, x):
    #             raise ValidationError(message)
    #     self._validators.append(_)
    #     return self

    def email(self, message: ErrorMessage = "email") -> Self:
        def _(x: str):
            if not re.match(rEmail_pattern, x):
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def url(self, message: ErrorMessage = "url") -> Self:
        def _(x: str):
            if not re.match(rUrl_pattern, x):
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def uuid(self, message: ErrorMessage = "uuid") -> Self:
        def _(x: str):
            if not re.match(rUUID_pattern, x):
                raise ValidationError(message)

        self._validators.append(_)
        return self

    # def datetime(self, message: ErrorMessage, precision: int, allow_offset: bool = False):
    #     def _(x: str):
    #         if ...:
    #             raise ValidationError(message)
    #     self._validators.append(_)
    #     return self

    def ensure(self):
        def _(x: str):
            if not x:
                return ""

    # def trim(self, message: ErrorMessage):
    #     def _(x: str):
    #         if ...:
    #             raise ValidationError(message)
    #     self._validators.append(_)
    #     return self

    def lowercase(self, message: ErrorMessage = "lowercase"):
        def _(x: str):
            if x.lower() != x:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def uppercase(self, message: ErrorMessage = "uppercase"):
        def _(x: str):
            if x.upper() != x:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def nullable(self, message: ErrorMessage = "nullable") -> Self:
        self._type = (str, None)
        return self


@dataclass
class NumberSchema(Schema):
    _type: Any = field(init=False, default=(float, int))

    def le(self, limit: int, message: ErrorMessage = "le") -> Self:
        def _(x: Union[int, float]):
            if x < limit:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def ge(self, limit: int, message: ErrorMessage = "ge") -> Self:
        def _(x: Union[int, float]):
            if x > limit:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def lt(self, limit: int, message: ErrorMessage = "lt") -> Self:
        def _(x: Union[int, float]):
            if x <= limit:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def gt(self, limit: int, message: ErrorMessage = "gt") -> Self:
        def _(x: Union[int, float]):
            if x >= limit:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def positive(self, message: ErrorMessage = "positive") -> Self:
        return self.gt(0, message)

    def negative(self, message: ErrorMessage = "negative") -> Self:
        return self.lt(0, message)

    def integer(self, message: ErrorMessage = "integer") -> Self:
        def _(x: Union[int, float]):
            if (x % 1) != 0:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    # def truncate(self):
    #     ...

    # def round(self, method: Literal['ceil', 'floor', 'round', 'trunc']) -> Self:
    #     self._transforms

    def multiple_of(self, multiplier: Union[int, float], message: ErrorMessage = "multiple_of") -> Self:
        def _(x: Union[int, float]):
            if x % multiplier != 0:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def nullable(self, message: ErrorMessage = "nullable") -> Self:
        self._type = (int, float, None)
        return self


@dataclass
class ObjSchema(Schema):
    _type: Any = dict
    _fields: Dict[str, Schema] = field(init=False, default_factory=dict)

    def shape(self, shape: Dict[str, Schema], message: ErrorMessage = "shape") -> Self:
        if not isinstance(shape, dict):
            raise ValidationError("shape must be a dictionary")
        if not all([isinstance(item, Schema) for item in shape.values()]):
            raise ValidationError("all shape items must be of type of Schema")
        self._fields = shape
        return self

    def validate(self, value: Dict[str, Any], path: str = ""):
        super().validate(value, path)
        self._validate_shape(value, path)

    def _validate_shape(self, value: Dict[str, Any], path: str = ""):

        for k, f in self._fields.items():
            path_ = ".".join((path, k))
            if not self._fields[k].optional and not k in value:
                raise ValidationError(f"key is required", path_)
            if k in value:
                self._fields[k].validate(value[k], path_)

    def __getitem__(self, item):
        return self._fields[item]


@dataclass
class ArrayShema(Schema):
    _type: Any = list
    _fields: List[Any] = field(init=False, default_factory=list)
    _type_of: Any = Any

    def of(self, type_: Schema, message: ErrorMessage = "of") -> Self:
        if not isinstance(type_, Schema):
            raise ValidationError("type_ must be a Schema")
        self._type_of = type_
        return self

    def length(self, limit: int, message: ErrorMessage = "length") -> Self:
        def _(x: str):
            if len(x) != limit:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def min(self, limit: int, message: ErrorMessage = "min") -> Self:
        def _(x: str):
            if len(x) < limit:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def max(self, limit: int, message: ErrorMessage = "max") -> Self:
        def _(x: str):
            if len(x) > limit:
                raise ValidationError(message)

        self._validators.append(_)
        return self

    def validate(self, value: List[Any], path: str = ""):
        super().validate(value, path)
        self._validate_array(value, path)

    def _validate_array(self, value: List[Any], path: str = ""):
        for i, v in enumerate(value):
            path_ = path + f"[{i}]"
            try:
                self._type_of.validate(v, path_)
            except ValidationError as err:
                raise ValidationError(err.message, path_)


string = StringSchema
number = NumberSchema
obj = ObjSchema
array = ArrayShema

if __name__ == "__main__":
    s = string().max(5).min(2).lowercase()
    n = number().required().integer().ge(100).le(10).multiple_of(30)
    l = array().required().of(s).min(2)

    s.validate("ab")
    n.validate(60)

    shp = obj().shape({
        's': s,
        'n': n,

        'shp': obj().shape({
            's': s,
            'n': n,
            'l': l,
        }).required()
    })

    # shp.validate({'s': "ab", 'n': 60})

    shp.validate({
        's': "ab",
        'n': 60,
        "shp": {
            'n': 60,
            'l': ['ab', 'b'],
        }
    })
