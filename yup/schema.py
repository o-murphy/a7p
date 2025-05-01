from dataclasses import field, dataclass

from typing_extensions import (
    Any,
    Self,
    List,
    Optional,
    Type, )

from yup.locale import locale
from yup.types import TransformFunc, ValidatorFunc
from yup.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('Schema',)


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
