from dataclasses import dataclass

from typing_extensions import Self

from yup.locale import locale
from yup.schema import Schema
from yup.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('_IterableSchema',)


@dataclass
class _IterableSchema(Schema):

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
