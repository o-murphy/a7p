from dataclasses import dataclass, field

from typing_extensions import Any, Dict, Self, Type

from yup.locale import locale
from yup.schema import Schema
from yup.util.concat_path import concat_path
from yup.validation_error import ValidationError, Constraint

__all__ = ('ObjSchema',)


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
