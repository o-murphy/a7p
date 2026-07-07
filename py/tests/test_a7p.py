import pytest

import a7p
from a7p.exceptions import A7PChecksumError, A7PError


def test_loads_dumps_roundtrip(raw_payload_bytes):
    payload = a7p.loads(raw_payload_bytes)
    rebuilt = a7p.dumps(payload)
    assert rebuilt == raw_payload_bytes


def test_load_dump_roundtrip(tmp_path, valid_a7p_path):
    with open(valid_a7p_path, "rb") as fp:
        payload = a7p.load(fp)

    out_path = tmp_path / "roundtrip.a7p"
    with open(out_path, "wb") as fp:
        a7p.dump(payload, fp)

    with open(out_path, "rb") as fp:
        reloaded = a7p.load(fp)

    assert reloaded == payload


def test_json_roundtrip(bc_ok_payload):
    as_json = a7p.to_json(bc_ok_payload)
    assert a7p.from_json(as_json) == bc_ok_payload


def test_dict_roundtrip(bc_ok_payload):
    as_dict = a7p.to_dict(bc_ok_payload)
    assert a7p.from_dict(as_dict) == bc_ok_payload


def test_loads_rejects_empty_payload():
    with pytest.raises(A7PError):
        a7p.loads(b"")


def test_loads_rejects_bad_checksum(raw_payload_bytes):
    corrupted = b"0" * 32 + raw_payload_bytes[32:]
    with pytest.raises(A7PChecksumError):
        a7p.loads(corrupted)
