import hashlib
import json
from typing import BinaryIO

from google.protobuf.json_format import MessageToJson, MessageToDict, Parse

from a7p import profedit_pb2
from a7p import protovalidate
from a7p import exceptions
from a7p.spec_validator import validate_spec


def loads(string: bytes, validate_: bool = True, fail_fast: bool = False):
    data = string[32:]
    md5_hash = hashlib.md5(data).hexdigest()
    if md5_hash == string[:32].decode():
        payload = profedit_pb2.Payload()
        payload.ParseFromString(data)
        if validate_:
            validate(payload, fail_fast)
        return payload
    else:
        raise exceptions.A7PChecksumError("Input data is missing for MD5 hashing")


def load(file: BinaryIO, validate_: bool = True, fail_fast: bool = False) -> profedit_pb2.Payload:
    string = file.read()
    return loads(string, validate_, fail_fast)


def dumps(payload: profedit_pb2.Payload, validate_: bool = True, fail_fast: bool = False) -> bytes:
    if validate_:
        validate(payload, fail_fast)
    data = payload.SerializeToString()
    md5_hash = hashlib.md5(data).hexdigest().encode()
    return md5_hash + data


def dump(payload: profedit_pb2.Payload, file: BinaryIO, validate_: bool = True, fail_fast: bool = False) -> None:
    data = dumps(payload, validate_, fail_fast)
    file.write(data)


def to_json(payload: profedit_pb2.Payload) -> str:
    return MessageToJson(payload)


def from_json(json_data: str) -> profedit_pb2.Payload:
    return Parse(json_data, profedit_pb2.Payload())


def to_dict(payload: profedit_pb2.Payload) -> dict:
    return MessageToDict(payload, including_default_value_fields=True)


def from_dict(data: dict) -> profedit_pb2.Payload:
    return Parse(json.dumps(data), profedit_pb2.Payload())


def validate(payload: profedit_pb2.Payload, fail_fast: bool = False):
    violations = {
        'violations': []
    }

    is_errors = False

    try:
        protovalidate.validate(payload)
    except protovalidate.ValidationError as err:
        proto_error = exceptions.A7PProtoValidationError(
            "Proto validation error",
            payload,
            err.violations
        )
        if fail_fast:
            raise proto_error
        is_errors = True
        violations['proto_violations'] = proto_error.proto_violations
        violations['violations'].append(
            exceptions.Violation(
                "Proto validation error",
                "Validation failed during proto validation",
                ""
            )
        )

    try:
        validate_spec(payload)
    except exceptions.A7PSpecValidationError as err:
        if fail_fast:
            raise err
        is_errors = True
        violations['spec_violations'] = err.spec_violations
        violations['violations'].append(
            exceptions.Violation(
                "Spec validation error",
                "Validation failed during spec validation",
                ""
            )
        )

    # Raise the final validation error if there are violations
    if is_errors:
        raise exceptions.A7PValidationError(
            "Validation error",
            payload,
            violations=violations['violations'],  # Загальний список порушень
            proto_violations=violations.get('proto_violations'),
            spec_violations=violations.get('spec_violations')
        )


__all__ = (
    'loads',
    'dumps',
    'load',
    'dump',
    'from_json',
    'to_json',
    'from_dict',
    'to_dict',
    'validate',
)

if __name__ == '__main__':
    pass
