import re
from dataclasses import dataclass, field

from typing_extensions import Any, List, Self, Optional, Union, Callable

__all__ = (
    'ErrorMessage',
    'ValidationError',
    'Constraint',
)

ErrorMessage = Union[str, Callable[[Any | List[Any]], str]]


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
