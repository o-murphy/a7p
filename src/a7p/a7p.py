"""
This module provides functions for serializing, deserializing, and validating `profedit_pb2.Payload` objects,
as well as converting between various formats such as JSON and dictionaries.

Functions:
    loads: Deserializes bytes data into a Payload object and validates it.
    load: Reads a file, deserializes the contents into a Payload object, and validates it.
    dumps: Serializes a Payload object into bytes, including an MD5 hash.
    dump: Serializes a Payload object and writes it to a file.
    to_json: Converts a Payload object to a JSON string.
    from_json: Converts a JSON string to a Payload object.
    to_dict: Converts a Payload object to a dictionary.
    from_dict: Converts a dictionary to a Payload object.
    validate: Validates a Payload object against proto and spec validation rules.
"""

import hashlib
import json
from typing import BinaryIO

from google.protobuf.json_format import MessageToJson, MessageToDict, Parse

from a7p import profedit_pb2
from a7p import protovalidate
from a7p import exceptions
from a7p.spec_validator import validate_spec


def loads(string: bytes, validate_: bool = True, fail_fast: bool = False) -> profedit_pb2.Payload:
    """
    Deserializes byte data into a Payload object and validates it.

    Args:
        string (bytes): The serialized byte data, with an MD5 hash as a prefix.
        validate_ (bool): Flag indicating whether to validate the payload. Default is True.
        fail_fast (bool): Flag indicating whether to raise errors immediately on validation failure. Default is False.

    Returns:
        profedit_pb2.Payload: The deserialized Payload object.

    Raises:
        A7PChecksumError: If the MD5 hash does not match the data.
        A7PValidationError: If validation fails.
    """
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
    """
    Reads a file, deserializes the contents into a Payload object, and validates it.

    Args:
        file (BinaryIO): The file-like object to read from.
        validate_ (bool): Flag indicating whether to validate the payload. Default is True.
        fail_fast (bool): Flag indicating whether to raise errors immediately on validation failure. Default is False.

    Returns:
        profedit_pb2.Payload: The deserialized Payload object.

    Raises:
        A7PChecksumError: If the MD5 hash does not match the data.
        A7PValidationError: If validation fails.
    """
    string = file.read()
    return loads(string, validate_, fail_fast)


def dumps(payload: profedit_pb2.Payload, validate_: bool = True, fail_fast: bool = False) -> bytes:
    """
    Serializes a Payload object into bytes, including an MD5 hash.

    Args:
        payload (profedit_pb2.Payload): The Payload object to serialize.
        validate_ (bool): Flag indicating whether to validate the payload. Default is True.
        fail_fast (bool): Flag indicating whether to raise errors immediately on validation failure. Default is False.

    Returns:
        bytes: The serialized byte data, with an MD5 hash as a prefix.

    Raises:
        A7PValidationError: If validation fails.
    """
    if validate_:
        validate(payload, fail_fast)
    data = payload.SerializeToString()
    md5_hash = hashlib.md5(data).hexdigest().encode()
    return md5_hash + data


def dump(payload: profedit_pb2.Payload, file: BinaryIO, validate_: bool = True, fail_fast: bool = False) -> None:
    """
    Serializes a Payload object and writes it to a file.

    Args:
        payload (profedit_pb2.Payload): The Payload object to serialize.
        file (BinaryIO): The file-like object to write to.
        validate_ (bool): Flag indicating whether to validate the payload. Default is True.
        fail_fast (bool): Flag indicating whether to raise errors immediately on validation failure. Default is False.

    Returns:
        None

    Raises:
        A7PValidationError: If validation fails.
    """
    data = dumps(payload, validate_, fail_fast)
    file.write(data)


def to_json(payload: profedit_pb2.Payload) -> str:
    """
    Converts a Payload object to a JSON string.

    Args:
        payload (profedit_pb2.Payload): The Payload object to convert.

    Returns:
        str: The JSON string representation of the Payload object.
    """
    return MessageToJson(payload,
                         including_default_value_fields=True,
                         preserving_proto_field_name=True)


def from_json(json_data: str) -> profedit_pb2.Payload:
    """
    Converts a JSON string to a Payload object.

    Args:
        json_data (str): The JSON string to convert.

    Returns:
        profedit_pb2.Payload: The deserialized Payload object.
    """
    return Parse(json_data, profedit_pb2.Payload())


def to_dict(payload: profedit_pb2.Payload) -> dict:
    """
    Converts a Payload object to a dictionary.

    Args:
        payload (profedit_pb2.Payload): The Payload object to convert.

    Returns:
        dict: The dictionary representation of the Payload object.
    """
    return MessageToDict(payload,
                         including_default_value_fields=True,
                         preserving_proto_field_name=True)


def from_dict(data: dict) -> profedit_pb2.Payload:
    """
    Converts a dictionary to a Payload object.

    Args:
        data (dict): The dictionary to convert.

    Returns:
        profedit_pb2.Payload: The deserialized Payload object.
    """
    return Parse(json.dumps(data), profedit_pb2.Payload())


def validate(payload: profedit_pb2.Payload, fail_fast: bool = False) -> None:
    """
    Validates a Payload object against proto and spec validation rules.

    Args:
        payload (profedit_pb2.Payload): The Payload object to validate.
        fail_fast (bool): Flag indicating whether to raise errors immediately on validation failure. Default is False.

    Returns:
        None

    Raises:
        A7PProtoValidationError: If there are proto validation errors.
        A7PSpecValidationError: If there are spec validation errors.
        A7PValidationError: If there are any violations.
    """
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
