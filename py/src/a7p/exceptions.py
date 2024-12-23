"""
This module defines custom error classes, data classes, and utility functions for
handling validation violations in the A7P project. It includes various types of
violations, error handling, and logic for extracting violations from protocol
buffers related to validation.

Classes:
    Violation: Represents a violation with a specific path, value, and reason.
    ProtoViolation: Represents a violation extracted from protocol buffer data.
    SpecViolation: Represents a specification-related violation.
    A7PError: Base class for all A7P-related errors.
    A7PDataError: A subclass of A7PError related to data issues.
    A7PChecksumError: A subclass of A7PDataError for checksum-related errors.
    A7PValidationError: A subclass of A7PDataError for validation-related errors.
    A7PProtoValidationError: A subclass of A7PValidationError for protocol validation errors.
    A7PSpecValidationError: A subclass of A7PValidationError for specification validation errors.
    A7PSpecTypeError: A subclass of A7PDataError for errors related to specification type mismatches.

Functions:
    _extract_violation: Extracts a violation from an expression_pb2.Violation object.
    _extract_protovalidate_violations: Extracts a list of ProtoViolation from an expression_pb2.Violations object.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Type

from a7p.buf.validate import expression_pb2
from a7p import profedit_pb2
from a7p.logger import logger


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


@dataclass
class ProtoViolation(Violation):
    """
    Represents a violation extracted from protocol buffer data, inheriting from Violation.

    Inherits all attributes and methods from Violation.
    """
    pass
    # def __init__(self, path: str, value: any, reason: str) -> None:
    #     self.path = Path("~/", *path.split("."))
    #     self.value = value
    #     self.reason = reason


@dataclass
class SpecViolation(Violation):
    """
    Represents a specification-related violation, inheriting from Violation.

    Inherits all attributes and methods from Violation.
    """
    pass


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
        violations (list[Violation]): A list of general violations.
        proto_violations (list[ProtoViolation]): A list of protocol validation violations.
        spec_violations (list[SpecViolation]): A list of specification validation violations.
    """

    def __init__(self, msg: str, payload: profedit_pb2.Payload,
                 violations: list[Violation] = None,
                 proto_violations: list[ProtoViolation] = None,
                 spec_violations: list[SpecViolation] = None):
        """
        Initializes the validation error with the provided message, payload, and violations.

        Args:
            msg (str): The error message.
            payload (profedit_pb2.Payload): The payload data.
            violations (list[Violation], optional): A list of violations.
            proto_violations (list[ProtoViolation], optional): A list of protocol validation violations.
            spec_violations (list[SpecViolation], optional): A list of specification validation violations.
        """
        super().__init__(msg)
        self.payload = payload
        self.violations = violations or []
        self.proto_violations = proto_violations or []
        self.spec_violations = spec_violations or []

    @property
    def all_violations(self) -> list[Violation]:
        """
        Combines all types of violations into a single list.

        Returns:
            list[Violation]: A combined list of violations.
        """
        return self.violations + self.proto_violations + self.spec_violations


class A7PProtoValidationError(A7PValidationError):
    """
    A subclass of A7PValidationError for errors specifically related to protocol validation.

    Args:
        msg (str): The error message.
        payload (profedit_pb2.Payload): The payload data associated with the error.
        violations (expression_pb2.Violations): The violations related to the protocol validation.
    """

    def __init__(self, msg: str, payload: profedit_pb2.Payload, violations: expression_pb2.Violations):
        """
        Initializes the protocol validation error with the provided message, payload, and violations.

        Args:
            msg (str): The error message.
            payload (profedit_pb2.Payload): The payload data.
            violations (expression_pb2.Violations): The violations related to the protocol validation.
        """
        super().__init__(msg, payload, proto_violations=_extract_protovalidate_violations(violations))


class A7PSpecValidationError(A7PValidationError):
    """
    A subclass of A7PValidationError for errors specifically related to specification validation.

    Args:
        msg (str): The error message.
        payload (any): The payload data associated with the error.
        violations (list[SpecViolation]): A list of specification violations.
    """

    def __init__(self, msg: str, payload, violations: list[SpecViolation]):
        """
        Initializes the specification validation error with the provided message, payload, and violations.

        Args:
            msg (str): The error message.
            payload (any): The payload data.
            violations (list[SpecViolation]): A list of specification violations.
        """
        super().__init__(msg, payload, spec_violations=violations)


class A7PSpecTypeError(A7PDataError):
    """
    A subclass of A7PDataError for errors related to type mismatches in the specification.

    Attributes:
        expected_types (tuple[Type, ...]): A tuple of expected types.
        actual_type (Type): The actual type that was encountered.
        message (str): The error message indicating the type mismatch.
    """

    def __init__(self, expected_types: tuple[Type, ...] = None, actual_type: Type = None):
        """
        Initializes the type error with the expected types, actual type, and an error message.

        Args:
            expected_types (tuple[Type, ...], optional): The expected types for the value.
            actual_type (Type, optional): The actual type that was encountered.
        """
        self.expected_types = expected_types or "UNKNOWN"
        self.actual_type = actual_type or "UNKNOWN"
        self.message = f"expected value to be one of types: {[t.__name__ for t in expected_types]}, " \
                       f"but got {actual_type.__name__} instead."
        super().__init__(self.message, self.expected_types, self.actual_type)


def _extract_violation(violation: expression_pb2.Violation) -> ProtoViolation:
    """
    Extracts a violation from an expression_pb2.Violation object.

    Args:
        violation (expression_pb2.Violation): The violation object to extract data from.

    Returns:
        ProtoViolation: The extracted ProtoViolation object.

    Raises:
        TypeError: If the provided violation is not an instance of expression_pb2.Violation.
    """
    if not isinstance(violation, expression_pb2.Violation):
        raise TypeError("Expected an instance of expression_pb2.Violation, but got a different type.")

    field_path = None
    constraint_id = None
    message = None

    # Iterate through all fields in the violation
    for violation_field, violation_value in violation.ListFields():
        if violation_field.name == "field_path":
            field_path = violation_value
        elif violation_field.name == "field":
            field_path = violation_value
        elif violation_field.name == "constraint_id":
            constraint_id = violation_value
        elif violation_field.name == "message":
            message = violation_value
        else:
            logger.warning(f"Unknown field: {violation_field.name} {violation_value}")

    return ProtoViolation(field_path, constraint_id, message)


def _extract_protovalidate_violations(violations: expression_pb2.Violations) -> list[ProtoViolation]:
    """
    Extracts a list of ProtoViolation from an expression_pb2.Violations object.

    Args:
        violations (expression_pb2.Violations): The violations object containing multiple violations.

    Returns:
        list[ProtoViolation]: A list of ProtoViolation objects extracted from the input.

    Raises:
        TypeError: If the provided violations object is not an instance of expression_pb2.Violations.
    """
    if not isinstance(violations, expression_pb2.Violations):
        raise TypeError("Expected an instance of expression_pb2.Violations, but got a different type.")

    extracted_violations = []
    for field, value in violations.ListFields():
        if field.name == "violations":  # Ensure we are handling the violations field
            for violation in value:  # Iterate over each Violation object
                extracted_violations.append(
                    _extract_violation(violation)
                )  # Pass the violation to the function

    return extracted_violations  # Ensure the violations are returned


__all__ = [
    'SpecViolation',
    'A7PError',
    'A7PDataError',
    'A7PChecksumError',
    'A7PValidationError',
    'A7PProtoValidationError',
    'A7PSpecValidationError',
    'A7PSpecTypeError',
    '_extract_violation',
    '_extract_protovalidate_violations'
]
