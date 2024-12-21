from dataclasses import dataclass
from pathlib import Path
from typing import Type

from a7p.buf.validate import expression_pb2
from a7p import profedit_pb2
from a7p.logger import logger


@dataclass
class Violation:
    path: Path | str
    value: any
    reason: str

    def format(self) -> str:
        is_stringer = isinstance(self.value, (str, int, float, bool))
        path__ = f"Path    :  {self.path.as_posix() if isinstance(self.path, Path) else self.path}"
        value_ = f"Value   :  {self.value if is_stringer else '<object>'}"
        reason = f"Reason  :  {self.reason}"
        return "\n\t".join(["Violation:", path__, value_, reason])


@dataclass
class ProtoViolation(Violation):
    pass


@dataclass
class SpecViolation(Violation):
    pass


class A7PError(RuntimeError):
    pass


class A7PDataError(A7PError):
    pass


class A7PChecksumError(A7PDataError):
    pass


class A7PValidationError(A7PDataError):
    def __init__(self, msg: str, payload: profedit_pb2.Payload,
                 violations: list[Violation] = None,
                 proto_violations: list[ProtoViolation] = None,
                 spec_violations: list[SpecViolation] = None,
                 ):
        super().__init__(msg)
        self.payload = payload
        self.violations = violations or []
        self.proto_violations = proto_violations or []
        self.spec_violations = spec_violations or []

    @property
    def all_violations(self) -> list[Violation]:
        return self.violations + self.proto_violations + self.spec_violations


class A7PProtoValidationError(A7PValidationError):
    def __init__(self, msg: str, payload: profedit_pb2.Payload, violations: expression_pb2.Violations):
        super().__init__(msg, payload, proto_violations=_extract_protovalidate_violations(violations))


class A7PSpecValidationError(A7PValidationError):
    def __init__(self, msg: str, payload, violations: list[SpecViolation]):
        super().__init__(msg, payload, spec_violations=violations)


class A7PSpecTypeError(A7PDataError):
    def __init__(self, expected_types: tuple[Type, ...] = None, actual_type: Type = None):
        self.expected_types = expected_types or "UNKNOWN"
        self.actual_type = actual_type or "UNKNOWN"
        self.message = f"expected value to be one of types: {[t.__name__ for t in expected_types]}, "
        f"but got {actual_type.__name__} instead."
        super().__init__(self.message, self.expected_types, self.actual_type)


def _extract_violation(violation: expression_pb2.Violation) -> ProtoViolation:  # Pass violation explicitly
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
            logger.warning("Unknown field: {} {}" % violation_field.name, violation_value)
    return ProtoViolation(field_path, constraint_id, message)


def _extract_protovalidate_violations(violations: expression_pb2.Violations) -> list[ProtoViolation]:
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
