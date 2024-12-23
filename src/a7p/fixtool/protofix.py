from .fixtool import FixTool
from a7p.factory import A7PFactory
from .. import profedit_pb2


def fix_str_len_type(string: str, expected_len: int, default: str = "nil"):
    if isinstance(string, str):
        return string[:expected_len]
    return default[:expected_len]


def _fix_bullet_name(payload):
    payload.profile.bullet_name = fix_str_len_type(payload.profile.bullet_name, 50)


def _fix_cartridge_name(payload):
    payload.profile.cartridge_name = fix_str_len_type(payload.profile.cartridge_name, 50)


def _fix_profile_name(payload):
    payload.profile.profile_name = fix_str_len_type(payload.profile.profile_name, 50)


def _fix_user_note(payload):
    payload.profile.user_note = fix_str_len_type(payload.profile.user_note, 250,
                                                 "Warning: Restored profile")


def _fix_short_name_top(payload):
    payload.profile.short_name_top = fix_str_len_type(payload.profile.short_name_top, 8)


def _fix_short_name_bot(payload):
    payload.profile.short_name_bot = fix_str_len_type(payload.profile.short_name_bot, 8)


def _fix_zero_x(payload):
    payload.profile.zero_x = 0


def _fix_zero_y(payload):
    payload.profile.zero_y = 0


def _fix_sc_height(payload):
    payload.profile.sc_height = 90


def _fix_r_twist(payload):
    payload.profile.r_twist = 10


def _fix_c_muzzle_velocity(payload):
    payload.profile.c_muzzle_velocity = 8000


def _fix_c_zero_temperature(payload):
    payload.profile.c_zero_temperature = 15


def _fix_c_t_coeff(payload):
    payload.profile.c_t_coeff = 1000


def _fix_c_zero_distance_idx(payload):
    payload.profile.c_zero_distance_idx = 0


def _fix_c_zero_air_temperature(payload):
    payload.profile.c_zero_air_temperature = 15


def _fix_c_zero_air_pressure(payload):
    payload.profile.c_zero_air_pressure = 10000


def _fix_c_zero_air_humidity(payload):
    payload.profile.c_zero_air_pressure = 0


def _fix_c_zero_w_pitch(payload):
    payload.profile.c_zero_w_pitch = 0


def _fix_c_zero_p_temperature(payload):
    payload.profile.c_zero_p_temperature = 15


def _fix_b_diameter(payload):
    payload.profile.b_diameter = 338


def _fix_b_weight(payload):
    payload.profile.b_weight = 3000


def _fix_b_length(payload):
    payload.profile.b_length = 1700


def _fix_twist_dir(payload):
    payload.twist_dir = profedit_pb2.TwistDir.RIGHT


def _fix_bc_type(payload):
    # TODO: check coef_rows len and values to fix it
    payload.bc_type = profedit_pb2.GType.G7


def _fix_switches(payload):
    # TODO: check values and then try to fix
    # TODO: check min / max len
    ...


def _fix_coef_rows(payload):
    # TODO: check bc_type to fix it
    # TODO: check min / max len
    ...


def _fix_distances(payload):
    # TODO: check min / max len
    del payload.profile.distances[:]
    payload.profile.distances[:] = [int(d * 100) for d in A7PFactory.DistanceTable.LONG_RANGE.value]


def _fix_caliber(payload):
    payload.profile.caliber = fix_str_len_type(payload.profile.caliber, 50)


def _fix_device_uuid(payload):
    payload.profile.device_uuid = fix_str_len_type(payload.profile.device_uuid, 50, "")


protofix = FixTool()

protofix.register("profile.profile_name", _fix_short_name_top)
protofix.register("profile.cartridge_name", _fix_cartridge_name)
protofix.register("profile.bullet_name", _fix_bullet_name)
protofix.register("profile.user_note", _fix_user_note)

protofix.register("profile.short_name_top", _fix_short_name_top)
protofix.register("profile.short_name_bot", _fix_short_name_bot)

protofix.register("profile.zero_x", _fix_zero_x)
protofix.register("profile.zero_y", _fix_zero_y)

protofix.register("profile.sc_height", _fix_sc_height)
protofix.register("profile.r_twist", _fix_r_twist)

protofix.register("profile.c_muzzle_velocity", _fix_c_muzzle_velocity)
protofix.register("profile.c_zero_temperature", _fix_c_zero_temperature)
protofix.register("profile.c_t_coeff", _fix_c_t_coeff)
protofix.register("profile.c_zero_distance_idx", _fix_c_zero_distance_idx)
protofix.register("profile.c_zero_air_temperature", _fix_c_zero_air_temperature)
protofix.register("profile.c_zero_air_pressure", _fix_c_zero_air_pressure)
protofix.register("profile.c_zero_air_humidity", _fix_c_zero_air_humidity)
protofix.register("profile.c_zero_w_pitch", _fix_c_zero_w_pitch)
protofix.register("profile.c_zero_p_temperature", _fix_c_zero_p_temperature)

protofix.register("profile.b_diameter", _fix_b_diameter)
protofix.register("profile.b_weight", _fix_b_weight)
protofix.register("profile.b_length", _fix_b_length)

protofix.register("profile.twist_dir", _fix_twist_dir)
protofix.register("profile.bc_type", _fix_bc_type)

protofix.register("profile.switches", _fix_switches)
protofix.register("profile.distances", _fix_distances)
protofix.register("profile.coef_rows", _fix_coef_rows)
protofix.register("profile.caliber", _fix_caliber)
protofix.register("profile.device_uuid", _fix_device_uuid)
