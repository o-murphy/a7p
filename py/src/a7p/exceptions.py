"""
This module defines custom error classes and data classes for handling
validation violations in the A7P project.

Classes:
    Violation: Represents a violation with a specific path, value, and reason.
    A7PError: Base class for all A7P-related errors.
    A7PDataError: A subclass of A7PError related to data issues.
    A7PChecksumError: A subclass of A7PDataError for checksum-related errors.
    A7PValidationError: A subclass of A7PDataError for validation-related errors.
"""

from dataclasses import dataclass
from pathlib import Path

from a7p import profedit_pb2


@dataclass
class Violation:
    """
    Represents a violation with a specific path, value, and reason.

    Attributes:
        path (Path | str): The path associated with the violation.
        value (any): The value that caused the violation.
        reason (str): A description of why the violation occurred.
    """

    path: Path | str
    value: any
    reason: str

    def format(self) -> str:
        """
        Formats the violation into a string representation.

        Returns:
            str: The formatted string containing the path, value, and reason of the violation.
        """
        is_stringer = isinstance(self.value, (str, int, float, bool))
        path__ = f"Path    :  {self.path.as_posix() if isinstance(self.path, Path) else self.path}"
        value_ = f"Value   :  {self.value if is_stringer else '<object>'}"
        reason = f"Reason  :  {self.reason}"
        return "\n    ".join(["Violation:".ljust(10), path__, value_, reason])


class A7PError(RuntimeError):
    """
    Base class for all A7P-related errors.

    Inherits from RuntimeError.
    """

    pass


class A7PDataError(A7PError):
    """
    A subclass of A7PError that is raised for data-related errors.
    """

    pass


class A7PChecksumError(A7PDataError):
    """
    A subclass of A7PDataError for errors related to checksum validation.
    """

    pass


class A7PValidationError(A7PDataError):
    """
    A subclass of A7PDataError for errors related to validation issues.

    Attributes:
        msg (str): The error message.
        payload (profedit_pb2.Payload): The payload data associated with the validation error.
        violations (list[Violation]): A list of violations.
    """

    def __init__(
        self,
        msg: str,
        payload: profedit_pb2.Payload,
        violations: list[Violation] = None,
    ):
        """
        Initializes the validation error with the provided message, payload, and violations.

        Args:
            msg (str): The error message.
            payload (profedit_pb2.Payload): The payload data.
            violations (list[Violation], optional): A list of violations.
        """
        super().__init__(msg)
        self.payload = payload
        self.violations = violations or []


__all__ = [
    "Violation",
    "A7PError",
    "A7PDataError",
    "A7PChecksumError",
    "A7PValidationError",
]
