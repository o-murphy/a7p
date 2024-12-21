"""
Stubs for profedit_pb2
"""

from typing import List
from google.protobuf.message import Message

class Payload(Message):
    profile: 'Profile'


class CoefRow(Message):
    bc_cd: int
    mv: int


class SwPos(Message):
    c_idx: int
    reticle_idx: int
    zoom: int
    distance: int
    distance_from: 'DType'


class Profile(Message):
    profile_name: str
    cartridge_name: str
    bullet_name: str
    short_name_top: str
    short_name_bot: str
    user_note: str
    zero_x: int
    zero_y: int
    sc_height: int
    r_twist: int
    c_muzzle_velocity: int
    c_zero_temperature: int
    c_t_coeff: int
    c_zero_distance_idx: int
    c_zero_air_temperature: int
    c_zero_air_pressure: int
    c_zero_air_humidity: int
    c_zero_w_pitch: int
    c_zero_p_temperature: int
    b_diameter: int
    b_weight: int
    b_length: int
    twist_dir: 'TwistDir'
    bc_type: 'GType'
    switches: List['SwPos']
    distances: List[int]
    coef_rows: List['CoefRow']
    caliber: str
    device_uuid: str


class DType:
    VALUE: int
    INDEX: int


class GType:
    G1: int
    G7: int
    CUSTOM: int


class TwistDir:
    RIGHT: int
    LEFT: int
