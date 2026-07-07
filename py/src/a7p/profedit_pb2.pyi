from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

CUSTOM: GType
DESCRIPTOR: _descriptor.FileDescriptor
G1: GType
G7: GType
INDEX: DType
LEFT: TwistDir
RIGHT: TwistDir
VALUE: DType

class CoefRow(_message.Message):
    __slots__ = ["bc_cd", "mv"]
    BC_CD_FIELD_NUMBER: _ClassVar[int]
    MV_FIELD_NUMBER: _ClassVar[int]
    bc_cd: int
    mv: int
    def __init__(self, bc_cd: _Optional[int] = ..., mv: _Optional[int] = ...) -> None: ...

class Payload(_message.Message):
    __slots__ = ["profile"]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    profile: Profile
    def __init__(self, profile: _Optional[_Union[Profile, _Mapping]] = ...) -> None: ...

class Profile(_message.Message):
    __slots__ = ["b_diameter", "b_length", "b_weight", "bc_type", "bullet_name", "c_muzzle_velocity", "c_t_coeff", "c_zero_air_humidity", "c_zero_air_pressure", "c_zero_air_temperature", "c_zero_distance_idx", "c_zero_p_temperature", "c_zero_temperature", "c_zero_w_pitch", "caliber", "cartridge_name", "coef_rows", "device_uuid", "distances", "profile_name", "r_twist", "sc_height", "short_name_bot", "short_name_top", "switches", "twist_dir", "user_note", "zero_x", "zero_y"]
    BC_TYPE_FIELD_NUMBER: _ClassVar[int]
    BULLET_NAME_FIELD_NUMBER: _ClassVar[int]
    B_DIAMETER_FIELD_NUMBER: _ClassVar[int]
    B_LENGTH_FIELD_NUMBER: _ClassVar[int]
    B_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    CALIBER_FIELD_NUMBER: _ClassVar[int]
    CARTRIDGE_NAME_FIELD_NUMBER: _ClassVar[int]
    COEF_ROWS_FIELD_NUMBER: _ClassVar[int]
    C_MUZZLE_VELOCITY_FIELD_NUMBER: _ClassVar[int]
    C_T_COEFF_FIELD_NUMBER: _ClassVar[int]
    C_ZERO_AIR_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    C_ZERO_AIR_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    C_ZERO_AIR_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    C_ZERO_DISTANCE_IDX_FIELD_NUMBER: _ClassVar[int]
    C_ZERO_P_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    C_ZERO_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    C_ZERO_W_PITCH_FIELD_NUMBER: _ClassVar[int]
    DEVICE_UUID_FIELD_NUMBER: _ClassVar[int]
    DISTANCES_FIELD_NUMBER: _ClassVar[int]
    PROFILE_NAME_FIELD_NUMBER: _ClassVar[int]
    R_TWIST_FIELD_NUMBER: _ClassVar[int]
    SC_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_BOT_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_TOP_FIELD_NUMBER: _ClassVar[int]
    SWITCHES_FIELD_NUMBER: _ClassVar[int]
    TWIST_DIR_FIELD_NUMBER: _ClassVar[int]
    USER_NOTE_FIELD_NUMBER: _ClassVar[int]
    ZERO_X_FIELD_NUMBER: _ClassVar[int]
    ZERO_Y_FIELD_NUMBER: _ClassVar[int]
    b_diameter: int
    b_length: int
    b_weight: int
    bc_type: GType
    bullet_name: str
    c_muzzle_velocity: int
    c_t_coeff: int
    c_zero_air_humidity: int
    c_zero_air_pressure: int
    c_zero_air_temperature: int
    c_zero_distance_idx: int
    c_zero_p_temperature: int
    c_zero_temperature: int
    c_zero_w_pitch: int
    caliber: str
    cartridge_name: str
    coef_rows: _containers.RepeatedCompositeFieldContainer[CoefRow]
    device_uuid: str
    distances: _containers.RepeatedScalarFieldContainer[int]
    profile_name: str
    r_twist: int
    sc_height: int
    short_name_bot: str
    short_name_top: str
    switches: _containers.RepeatedCompositeFieldContainer[SwPos]
    twist_dir: TwistDir
    user_note: str
    zero_x: int
    zero_y: int
    def __init__(self, profile_name: _Optional[str] = ..., cartridge_name: _Optional[str] = ..., bullet_name: _Optional[str] = ..., short_name_top: _Optional[str] = ..., short_name_bot: _Optional[str] = ..., user_note: _Optional[str] = ..., zero_x: _Optional[int] = ..., zero_y: _Optional[int] = ..., sc_height: _Optional[int] = ..., r_twist: _Optional[int] = ..., c_muzzle_velocity: _Optional[int] = ..., c_zero_temperature: _Optional[int] = ..., c_t_coeff: _Optional[int] = ..., c_zero_distance_idx: _Optional[int] = ..., c_zero_air_temperature: _Optional[int] = ..., c_zero_air_pressure: _Optional[int] = ..., c_zero_air_humidity: _Optional[int] = ..., c_zero_w_pitch: _Optional[int] = ..., c_zero_p_temperature: _Optional[int] = ..., b_diameter: _Optional[int] = ..., b_weight: _Optional[int] = ..., b_length: _Optional[int] = ..., twist_dir: _Optional[_Union[TwistDir, str]] = ..., bc_type: _Optional[_Union[GType, str]] = ..., switches: _Optional[_Iterable[_Union[SwPos, _Mapping]]] = ..., distances: _Optional[_Iterable[int]] = ..., coef_rows: _Optional[_Iterable[_Union[CoefRow, _Mapping]]] = ..., caliber: _Optional[str] = ..., device_uuid: _Optional[str] = ...) -> None: ...

class SwPos(_message.Message):
    __slots__ = ["c_idx", "distance", "distance_from", "reticle_idx", "zoom"]
    C_IDX_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_FIELD_NUMBER: _ClassVar[int]
    RETICLE_IDX_FIELD_NUMBER: _ClassVar[int]
    ZOOM_FIELD_NUMBER: _ClassVar[int]
    c_idx: int
    distance: int
    distance_from: DType
    reticle_idx: int
    zoom: int
    def __init__(self, c_idx: _Optional[int] = ..., reticle_idx: _Optional[int] = ..., zoom: _Optional[int] = ..., distance: _Optional[int] = ..., distance_from: _Optional[_Union[DType, str]] = ...) -> None: ...

class DType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class GType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class TwistDir(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
