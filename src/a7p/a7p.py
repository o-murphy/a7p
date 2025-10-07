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
import warnings
from typing import BinaryIO

from google.protobuf.json_format import MessageToJson, MessageToDict, Parse

from a7p import exceptions
from a7p import profedit_pb2
from a7p import protovalidate
from a7p.spec_validator import validate_spec
from a7p.yupy_schema import validate as validate_yupy
from yupy import ValidationError as YupyValidationError

USE_PROTOVALIDATE = False
USE_SPEC_VALIDATOR = False
USE_YUPY_VALIDATOR = True


def setUseProtovalidate(flag: bool):
    if flag:
        warnings.warn("protovalidate", DeprecationWarning)
    global USE_PROTOVALIDATE
    USE_PROTOVALIDATE = flag


def setUseSpecValidator(flag: bool):
    if flag:
        warnings.warn("spec_validator", DeprecationWarning)
    global USE_SPEC_VALIDATOR
    USE_SPEC_VALIDATOR = flag


def setUseYupyValidator(flag: bool):
    global USE_YUPY_VALIDATOR
    USE_YUPY_VALIDATOR = flag


def loads(
    string: bytes, validate_: bool = True, fail_fast: bool = False
) -> profedit_pb2.Payload:
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


def load(
    file: BinaryIO, validate_: bool = True, fail_fast: bool = False
) -> profedit_pb2.Payload:
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


def dumps(
    payload: profedit_pb2.Payload, validate_: bool = True, fail_fast: bool = False
) -> bytes:
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


def dump(
    payload: profedit_pb2.Payload,
    file: BinaryIO,
    validate_: bool = True,
    fail_fast: bool = False,
) -> None:
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


def to_json(
    payload: profedit_pb2.Payload, preserving_proto_field_name: bool = True
) -> str:
    """
    Converts a Payload object to a JSON string.

    Args:
        payload (profedit_pb2.Payload): The Payload object to convert.
        preserving_proto_field_name:

    Returns:
        str: The JSON string representation of the Payload object.
    """
    return MessageToJson(
        payload,
        always_print_fields_with_no_presence=True,
        preserving_proto_field_name=preserving_proto_field_name,
    )


def from_json(json_data: str) -> profedit_pb2.Payload:
    """
    Converts a JSON string to a Payload object.

    Args:
        json_data (str): The JSON string to convert.

    Returns:
        profedit_pb2.Payload: The deserialized Payload object.
    """
    return Parse(json_data, profedit_pb2.Payload())


def to_dict(
    payload: profedit_pb2.Payload, preserving_proto_field_name: bool = True
) -> dict:
    """
    Converts a Payload object to a dictionary.

    Args:
        payload (profedit_pb2.Payload): The Payload object to convert.
        preserving_proto_field_name:

    Returns:
        dict: The dictionary representation of the Payload object.
    """
    return MessageToDict(
        payload,
        always_print_fields_with_no_presence=True,
        preserving_proto_field_name=preserving_proto_field_name,
    )


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
        _protovalidate (bool): DEPRECATED: Disabled by default, cause too slow and not effective

    Returns:
        None

    Raises:
        A7PProtoValidationError: If there are proto validation errors.
        A7PSpecValidationError: If there are spec validation errors.
        A7PValidationError: If there are any violations.
    """
    violations = {"violations": []}

    is_errors = False

    if USE_PROTOVALIDATE:
        try:
            protovalidate.validate(payload)
        except protovalidate.ValidationError as err:
            proto_error = exceptions.A7PProtoValidationError(
                "Proto validation error", payload, err.violations
            )
            if fail_fast:
                raise proto_error
            is_errors = True
            violations["proto_violations"] = proto_error.proto_violations
            violations["violations"].append(
                exceptions.Violation(
                    "Proto validation error",
                    "Validation failed during proto validation",
                    "",
                )
            )

    if USE_SPEC_VALIDATOR:
        try:
            validate_spec(payload)
        except exceptions.A7PSpecValidationError as err:
            if fail_fast:
                raise err
            is_errors = True
            violations["spec_violations"] = err.spec_violations
            violations["violations"].append(
                exceptions.Violation(
                    "Spec validation error",
                    "Validation failed during spec validation",
                    "",
                )
            )

    if USE_YUPY_VALIDATOR:
        try:
            validate_yupy(payload)
        except YupyValidationError as error:
            is_errors = True
            yupy_violations = []
            for err in error.errors:
                yupy_violations.append(
                    exceptions.Violation(
                        err.path,
                        err.invalid_value,
                        err.message,
                    )
                )
            violations["yupy_violations"] = yupy_violations
            violations["violations"].append(
                exceptions.Violation(
                    "Yupy validation error",
                    "Validation failed during yupy schema validation",
                    "",
                )
            )

        # raise NotImplementedError("yupy validation is not currently supported")

    # Raise the final validation error if there are violations
    if is_errors:
        raise exceptions.A7PValidationError(
            "Validation error",
            payload,
            violations=violations["violations"],  # Загальний список порушень
            proto_violations=violations.get("proto_violations"),
            spec_violations=violations.get("spec_violations"),
            yupy_violations=violations.get("yupy_violations"),
        )


__all__ = (
    "loads",
    "dumps",
    "load",
    "dump",
    "from_json",
    "to_json",
    "from_dict",
    "to_dict",
    "validate",
    "setUseProtovalidate",
)

if __name__ == "__main__":
    pass
