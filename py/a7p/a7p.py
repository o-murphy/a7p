import hashlib
import json
from typing import BinaryIO

from a7p import profedit_pb2
from google.protobuf.json_format import MessageToJson, MessageToDict, Parse
from a7p import protovalidate as validator

__all__ = ['A7PFile', 'A7PDataError']


class A7PDataError(Exception):
    pass


class A7PFile:

    @staticmethod
    def loads(string: bytes, validate: bool = True):
        data = string[32:]
        md5_hash = hashlib.md5(data).hexdigest()
        if md5_hash == string[:32].decode():
            profile = profedit_pb2.Payload()
            profile.ParseFromString(data)
            if validate:
                validator.validate(profile)
            return profile
        else:
            raise A7PDataError("Input data is missing for MD5 hashing")

    @staticmethod
    def load(file: BinaryIO, validate: bool = True) -> profedit_pb2.Payload:
        string = file.read()
        return A7PFile.loads(string, validate)

    @staticmethod
    def dumps(profile: profedit_pb2.Payload, validate: bool = True) -> bytes:
        if validate:
            validator.validate(profile)
        data = profile.SerializeToString()
        md5_hash = hashlib.md5(data).hexdigest().encode()
        return md5_hash + data

    @staticmethod
    def dump(profile: profedit_pb2.Payload, file: BinaryIO, validate: bool = True) -> None:
        data = A7PFile.dumps(profile, validate)
        file.write(data)

    @staticmethod
    def to_json(profile: profedit_pb2.Payload) -> str:
        return MessageToJson(profile)

    @staticmethod
    def from_json(json_data: str) -> profedit_pb2.Payload:
        return Parse(json_data, profedit_pb2.Payload())

    @staticmethod
    def to_dict(profile: profedit_pb2.Payload) -> dict:
        return MessageToDict(profile)

    @staticmethod
    def from_dict(data: dict) -> profedit_pb2.Payload:
        return Parse(json.dumps(data), profedit_pb2.Payload())


if __name__ == '__main__':
    with open('test.a7p', 'rb') as a7p:
        a7p_obj = A7PFile.load(a7p)
        a7p_dict = A7PFile.to_dict(a7p_obj)
        a7p_json = A7PFile.to_json(a7p_obj)
        a7p_by_dict = A7PFile.from_dict(a7p_dict)
        a7p_by_json = A7PFile.from_json(a7p_json)
