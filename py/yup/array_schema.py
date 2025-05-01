from dataclasses import dataclass, field

from typing_extensions import Any, Self, List, Type

from yup._iterable_schema import _IterableSchema
from yup.locale import locale
from yup.schema import Schema
from yup.util.concat_path import concat_path
from yup.validation_error import ErrorMessage, Constraint, ValidationError

__all__ = ('ArraySchema',)


@dataclass
class ArraySchema(_IterableSchema):
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
