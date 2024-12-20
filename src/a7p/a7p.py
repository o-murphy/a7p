import hashlib
import json
from typing import BinaryIO

from google.protobuf.json_format import MessageToJson, MessageToDict, Parse

from . import profedit_pb2
from . import protovalidate
from . import exceptions


def loads(string: bytes, validate_: bool = True):
    data = string[32:]
    md5_hash = hashlib.md5(data).hexdigest()
    if md5_hash == string[:32].decode():
        profile = profedit_pb2.Payload()
        profile.ParseFromString(data)
        if validate_:
            validate(profile)
        return profile
    else:
        raise exceptions.A7PChecksumError("Input data is missing for MD5 hashing")


def load(file: BinaryIO, validate_: bool = True) -> profedit_pb2.Payload:
    string = file.read()
    return loads(string, validate_)


def dumps(profile: profedit_pb2.Payload, validate_: bool = True) -> bytes:
    if validate_:
        validate(profile)
    data = profile.SerializeToString()
    md5_hash = hashlib.md5(data).hexdigest().encode()
    return md5_hash + data


def dump(profile: profedit_pb2.Payload, file: BinaryIO, validate_: bool = True) -> None:
    data = dumps(profile, validate_)
    file.write(data)


def to_json(profile: profedit_pb2.Payload) -> str:
    return MessageToJson(profile)


def from_json(json_data: str) -> profedit_pb2.Payload:
    return Parse(json_data, profedit_pb2.Payload())


def to_dict(profile: profedit_pb2.Payload) -> dict:
    return MessageToDict(profile, including_default_value_fields=True)


def from_dict(data: dict) -> profedit_pb2.Payload:
    return Parse(json.dumps(data), profedit_pb2.Payload())


def validate(profile: profedit_pb2.Payload):
    try:
        protovalidate.validate(profile)
    except protovalidate.ValidationError as e:
        raise exceptions.A7PProtoValidationError("Validation error", violations=e.violations) from e


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
