"""
Stubs for profedit_pb2
"""

from dataclasses import dataclass
from enum import IntEnum


@dataclass
class DType(IntEnum):
    VALUE = 0
    INDEX = 1


@dataclass
class CoefRow:
    bc_cd: int = None
    mv: int = None


@dataclass
class SwPos:
    c_idx: int = None
    reticle_idx: int = None
    zoom: int = None
    distance: int = None
    distance_from: DType  = None


class TwistDir(IntEnum):
    RIGHT = 0
    LEFT = 1


class GType(IntEnum):
    G1 = 0
    G7 = 1
    CUSTOM = 2


@dataclass
class Profile:
    profile_name: str = None
    cartridge_name: str = None
    bullet_name: str = None
    short_name_top: str = None
    short_name_bot: str = None
    user_note: str = None
    zero_x: int = None
    zero_y: int = None
    sc_height: int = None
    r_twist: int = None
    c_muzzle_velocity: int = None
    c_zero_temperature: int = None
    c_t_coeff: int = None
    c_zero_distance_idx: int = None
    c_zero_air_temperature: int = None
    c_zero_air_pressure: int = None
    c_zero_air_humidity: int = None
    c_zero_w_pitch: int = None
    c_zero_p_temperature: int = None
    b_diameter: int = None
    b_weight: int = None
    b_length: int = None
    twist_dir: TwistDir = None
    bc_type: GType = None
    switches: list[SwPos] = None
    distances: list[int] = None
    coef_rows: list[CoefRow] = None
    caliber: str = None
    device_uuid: str = None


@dataclass
class Payload:
    profile: Profile = None
