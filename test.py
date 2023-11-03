import hashlib
from typing import BinaryIO
from profedit_validate_pb2 import Payload
import protovalidate


def loads(string: bytes):
    data = string[32:]
    md5_hash = hashlib.md5(data).hexdigest()
    if md5_hash == string[:32].decode():
        profile = Payload()
        profile.ParseFromString(data)
        return profile
    else:
        raise ValueError


def load(file: BinaryIO) -> Payload:
    string = file.read()
    return loads(string)


with open('a7p/test.a7p', 'rb') as fp:
    payload = load(fp)


payload.profile.profile_name = "a" * 55

protovalidate.validate(payload)
