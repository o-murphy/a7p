from pathlib import Path

import pytest

import a7p

DATA_DIR = Path(__file__).parent / "data"

VALID_FIXTURES = ("bc_ok.a7p", "example.a7p", "example2.a7p", "test.a7p")
INVALID_FIXTURES = ("broken.a7p",)


@pytest.fixture
def data_dir() -> Path:
    return DATA_DIR


@pytest.fixture(params=VALID_FIXTURES)
def valid_a7p_path(request, data_dir) -> Path:
    return data_dir / request.param


@pytest.fixture(params=INVALID_FIXTURES)
def invalid_a7p_path(request, data_dir) -> Path:
    return data_dir / request.param


@pytest.fixture
def bc_ok_path(data_dir) -> Path:
    return data_dir / "bc_ok.a7p"


@pytest.fixture
def broken_path(data_dir) -> Path:
    return data_dir / "broken.a7p"


@pytest.fixture
def bc_ok_payload():
    with open(DATA_DIR / "bc_ok.a7p", "rb") as fp:
        return a7p.load(fp, validate_=False)


@pytest.fixture
def raw_payload_bytes() -> bytes:
    """A minimal serialized Payload (md5 hash + protobuf bytes), used for
    loads/dumps roundtrip and format-level (non-schema) tests."""
    with open(DATA_DIR / "test.a7p", "rb") as fp:
        return fp.read()


def _default_switch(**overrides) -> dict:
    switch = {
        "c_idx": 0,
        "distance_from": "VALUE",
        "distance": 100,
        "reticle_idx": 0,
        "zoom": 0,
    }
    switch.update(overrides)
    return switch


def _minimal_profile_dict() -> dict:
    """A profile dict whose values sit within every bound the schema
    validator currently enforces (mirrors the profedit.clj reference ranges)."""
    return {
        "profile": {
            "profile_name": "x",
            "cartridge_name": "x",
            "bullet_name": "x",
            "short_name_top": "x",
            "short_name_bot": "x",
            "caliber": "x",
            "device_uuid": "x",
            "user_note": "x",
            "zero_x": 0,
            "zero_y": 0,
            "distances": [100, 100, 100, 100],
            "switches": [_default_switch() for _ in range(4)],
            "sc_height": 0,
            "r_twist": 0,
            "twist_dir": "RIGHT",
            "c_muzzle_velocity": 100,
            "c_zero_temperature": 0,
            "c_t_coeff": 0,
            "c_zero_distance_idx": 0,
            "c_zero_air_temperature": 0,
            "c_zero_air_pressure": 3000,
            "c_zero_air_humidity": 0,
            "c_zero_w_pitch": 0,
            "c_zero_p_temperature": 0,
            "b_diameter": 1,
            "b_weight": 10,
            "b_length": 10,
            "bc_type": "G1",
            "coef_rows": [{"bc_cd": 0, "mv": 0}],
        }
    }


@pytest.fixture
def build_payload():
    """Factory fixture: build_payload(profile={"zoom": ...}) -> Payload.

    `profile` overrides are shallow-merged into a minimal, schema-valid
    profile dict. Use for targeted schema bound tests.
    """

    def _build(profile: dict = None):
        data = _minimal_profile_dict()
        if profile:
            data["profile"].update(profile)
        return a7p.from_dict(data)

    return _build


@pytest.fixture
def default_switch():
    return _default_switch
