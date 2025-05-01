from typing import Type, Any

from yup.locale import locale
from yup.schema import Schema
from yup.validation_error import ErrorMessage, Constraint, ValidationError

__all__ = ('Mixed',)


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
