import re
from dataclasses import dataclass, field


from typing_extensions import (
    Any,
    Callable,
    Union,
    Self,
    List,
    Dict,
    Optional,
    TypedDict,
    Type,
)

ErrorMessage = Union[str, Callable[[Any | List[Any]], str]]


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


def concat_path(path, item):
    # return path + "[%r]" % item
    if isinstance(item, str):
        if path == "":
            return item
        return ".".join((path, item))
    elif isinstance(item, int):
        return path + "[%r]" % item
    else:
        raise TypeError("Unsupported item type")


@dataclass
class Constraint:
    type: Optional[str]
    args: Any
    message: ErrorMessage = field(repr=False)

    @property
    def format_message(self):
        if callable(self.message):
            return self.message(self.args)
        return self.message


class ValidationError(ValueError):
    def __init__(
            self, constraint: Constraint, path: str = "", errors: List[Self] = None, *args
    ) -> None:
        self.path = re.sub(r"^\.", "", path)
        self.constraint = constraint
        self._errors = errors or []
        super().__init__(self.path, self.constraint, self._errors, *args)

    def __str__(self):
        return f"(path={repr(self.path)}, constraint={self.constraint}, message={repr(self.constraint.format_message)})"

    def __repr__(self):
        return "ValidationError%s" % self.__str__()

    @property
    def errors(self):
        yield self
        for error in self._errors:
            yield from error.errors

    @property
    def message(self):
        return f"{repr(self.path)}: {self.constraint.format_message}"

    @property
    def messages(self):
        for e in self.errors:
            yield e.message


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

Condition = Callable[[Any], bool]
TransformFunc = Callable[[Any], Any]
ValidatorFunc = Callable[[Any], None]


@dataclass
class Schema:
    _type: Type = field(default=Any)
    _transforms: List[TransformFunc] = field(init=False, default_factory=list)
    _validators: List[ValidatorFunc] = field(init=False, default_factory=list)
    _optional: bool = True
    _required: Optional[ErrorMessage] = locale["required"]
    _nullability: bool = False
    _not_nullable: ErrorMessage = locale["not_nullable"]

    @property
    def optional(self) -> bool:
        return self._optional

    def required(self, message: ErrorMessage = locale["required"]) -> Self:
        self._required = message
        self._optional = False
        return self

    def not_required(self) -> Self:
        self._optional = True
        return self

    def nullable(self) -> Self:
        self._nullability = True
        return self

    def not_nullable(self, message: ErrorMessage = locale["not_nullable"]) -> Self:
        self._nullability = False
        self._not_nullable = message
        return self

    def _nullable_check(self):
        if not self._nullability:
            raise ValidationError(
                Constraint("nullable", None, self._not_nullable),
            )

    def _type_check(self, value: Any):
        type_ = self._type
        if type_ is Any:
            return
        if not isinstance(value, type_):
            raise ValidationError(
                Constraint("type", (type_, type(value)), locale["type"])
            )

    def transform(self, func: TransformFunc) -> Self:
        self._transforms.append(func)
        return self

    def test(self, func: ValidatorFunc) -> Self:
        self._validators.append(func)
        return self

    def validate(self, value: Any, abort_early: bool = True, path: str = "") -> Any:
        try:
            if value is None:
                self._nullable_check()
                return

            self._type_check(value)

            # FIXME
            transformed = value
            for t in self._transforms:
                transformed = t(value)

            for v in self._validators:
                v(transformed)
        except ValidationError as err:
            raise ValidationError(err.constraint, path)


@dataclass
class _Iterable(Schema):

    def length(self, limit: int, message: ErrorMessage = locale["length"]) -> Self:
        def _(x):
            if len(x) != limit:
                raise ValidationError(Constraint("length", limit, message))

        return self.test(_)

    def min(self, limit: int, message: ErrorMessage = locale["min"]) -> Self:
        def _(x):
            if len(x) < limit:
                raise ValidationError(Constraint("min", limit, message))

        return self.test(_)

    def max(self, limit: int, message: ErrorMessage = locale["max"]) -> Self:
        def _(x):
            if len(x) > limit:
                raise ValidationError(Constraint("max", limit, message))

        return self.test(_)


@dataclass
class StringSchema(_Iterable):
    _type: Type = field(init=False, default=str)

    # def matches(self, regex: re.Pattern, message: ErrorMessage, exclude_empty: bool = False) -> Schema:
    #     def _(x: str):
    #         if not re.match(regex, x):
    #             raise ValidationError(message)
    #     self._validators.append(_)
    #     return self

    def email(self, message: ErrorMessage = locale["email"]) -> Self:
        def _(x: str):
            if not re.match(rEmail_pattern, x):
                raise ValidationError(Constraint("email", None, message))

        return self.test(_)

    def url(self, message: ErrorMessage = locale["url"]) -> Self:
        def _(x: str):
            if not re.match(rUrl_pattern, x):
                raise ValidationError(Constraint("url", None, message))

        return self.test(_)

    def uuid(self, message: ErrorMessage = locale["uuid"]) -> Self:
        def _(x: str):
            if not re.match(rUUID_pattern, x):
                raise ValidationError(Constraint("uuid", None, message))

        return self.test(_)

    # def datetime(self, message: ErrorMessage, precision: int, allow_offset: bool = False):
    #     def _(x: str):
    #         if ...:
    #             raise ValidationError(message)
    #     self._validators.append(_)
    #     return self

    def ensure(self):
        def _(x: str):
            return x if x else ""

        self._transforms.append(_)
        return self

    # def trim(self, message: ErrorMessage):
    #     def _(x: str):
    #         if ...:
    #             raise ValidationError(message)
    #     self._validators.append(_)
    #     return self

    def lowercase(self, message: ErrorMessage = locale["lowercase"]):
        def _(x: str):
            if x.lower() != x:
                raise ValidationError(Constraint("lowercase", None, message))

        return self.test(_)

    def uppercase(self, message: ErrorMessage = locale["uppercase"]):
        def _(x: str):
            if x.upper() != x:
                raise ValidationError(Constraint("uppercase", None, message))

        return self.test(_)


@dataclass
class NumberSchema(Schema):
    _type: Type = field(init=False, default=(float, int))

    def le(self, limit: int, message: ErrorMessage = locale["le"]) -> Self:
        def _(x: Union[int, float]):
            if x > limit:
                raise ValidationError(Constraint("le", limit, message))

        return self.test(_)

    def ge(self, limit: int, message: ErrorMessage = locale["ge"]) -> Self:
        def _(x: Union[int, float]):
            if x < limit:
                raise ValidationError(Constraint("ge", limit, message))

        return self.test(_)

    def lt(self, limit: int, message: ErrorMessage = locale["lt"]) -> Self:
        def _(x: Union[int, float]):
            if x >= limit:
                raise ValidationError(Constraint("lt", limit, message))

        return self.test(_)

    def gt(self, limit: int, message: ErrorMessage = locale["gt"]) -> Self:
        def _(x: Union[int, float]):
            if x <= limit:
                raise ValidationError(Constraint("gt", limit, message))

        return self.test(_)

    def positive(self, message: ErrorMessage = locale["positive"]) -> Self:
        return self.gt(0, message)

    def negative(self, message: ErrorMessage = locale["negative"]) -> Self:
        return self.lt(0, message)

    def integer(self, message: ErrorMessage = locale["integer"]) -> Self:
        def _(x: Union[int, float]):
            if (x % 1) != 0:
                raise ValidationError(Constraint("integer", None, message))

        return self.test(_)

    # def truncate(self):
    #     ...

    # def round(self, method: Literal['ceil', 'floor', 'round', 'trunc']) -> Self:
    #     self._transforms

    def multiple_of(
            self,
            multiplier: Union[int, float],
            message: ErrorMessage = locale["multiple_of"],
    ) -> Self:
        def _(x: Union[int, float]):
            if x % multiplier != 0:
                raise ValidationError(Constraint("multiple_of", multiplier, message))

        return self.test(_)


@dataclass
class ObjSchema(Schema):
    _type: Type = dict
    _fields: Dict[str, Schema] = field(init=False, default_factory=dict)

    def shape(self, fields: Dict[str, Schema]) -> Self:
        if not isinstance(fields, dict):
            raise ValidationError(
                Constraint("shape", None, locale["shape"])
            )
        if not all([isinstance(item, Schema) for item in fields.values()]):
            raise ValidationError(
                Constraint(
                    "shape_values", None, locale["shape_values"]  # Todo: key there
                )
            )
        self._fields = fields
        return self

    def validate(self, value: Dict[str, Any], abort_early: bool = True, path: str = ""):
        super().validate(value, abort_early, path)
        self._validate_shape(value, abort_early, path)

    def _validate_shape(self, value: Dict[str, Any], abort_early: bool = True, path: str = ""):
        errs = []
        for k, f in self._fields.items():
            path_ = concat_path(path, k)
            try:
                if not self._fields[k]._optional and not k in value:
                    raise ValidationError(
                        Constraint(
                            "required",
                            path_,
                            self._fields[k]._required,
                        ),
                        path_,
                    )
                if k in value:
                    self._fields[k].validate(value[k], abort_early, path_)
            except ValidationError as err:
                if abort_early:
                    raise ValidationError(err.constraint, path_)
                errs.append(err)
        if errs:
            raise ValidationError(
                Constraint(
                    'array',
                    path,
                    'invalid object'
                ),
                path, errs
            )

    def __getitem__(self, item: str) -> Schema:
        return self._fields[item]


@dataclass
class ArraySchema(_Iterable):
    _type: Type = (list, tuple)
    _fields: List[Any] = field(init=False, default_factory=list)
    _type_of: Schema = field(init=False, default_factory=Schema)

    def of(self, schema: Schema, message: ErrorMessage = locale["array_of"]) -> Self:
        if not isinstance(schema, Schema):
            raise ValidationError(Constraint("array_of", type(schema), message))
        self._type_of = schema
        return self

    def validate(self, value: List[Any], abort_early: bool = True, path: str = ""):
        super().validate(value, abort_early, path)
        self._validate_array(value, abort_early, path)

    def _validate_array(self, value: List[Any], abort_early: bool = True, path: str = ""):
        errs = []
        for i, v in enumerate(value):
            path_ = concat_path(path, i)
            try:
                self._type_of.validate(v, abort_early, path_)
            except ValidationError as err:
                if abort_early:
                    raise ValidationError(err.constraint, path_)
                else:
                    errs.append(err)
        if errs:
            raise ValidationError(
                Constraint(
                    'array',
                    path,
                    'invalid array'
                ),
                path, errs)

    def __getitem__(self, item: int) -> Schema:
        return self._fields[item]


class Mixed(Schema):
    _type: Type = Any

    def one_of(self, items, message: ErrorMessage = locale['one_of']):
        ...

        def _(x):
            if x not in items:
                raise ValidationError(
                    Constraint(
                        'one_of',
                        items,
                        message
                    )
                )

        return self.test(_)


string = StringSchema
number = NumberSchema
obj = ObjSchema
array = ArraySchema
mixed = Mixed

if __name__ == "__main__":

    s = string().max(5).min(2).lowercase()
    n = number().required().integer().ge(100).le(10).multiple_of(30)
    l = array().required().of(s).min(2)

    s.validate("ab")
    n.validate(60)

    shp = obj().shape(
        {
            "email": string().email().required(),
            "s": s,
            "n": n,
            "shp": obj()
            .shape(
                {
                    "s": s,
                    "n": n,
                    # 'l': l,
                    "o": obj().shape({"n": l}),
                }
            )
            .required(),
        }
    )

    # shp.validate({'s': "ab", 'n': 60})
    try:
        shp.validate(
            {
                "email": "a@gmail.com",
                "s": "wd",
                "n": 60,
                "shp": {"n": "a", "l": ["ab", "b"], "o": {"n": ["g", "g"]}},
            }, False
        )
    except ValidationError as err:

        for e in err.errors:
            print(str(e.path or "<None>") + ':')
            print('  ', e.constraint.format_message)

    m = mixed().one_of(['G1', 'G7'])
    m.validate('F')
