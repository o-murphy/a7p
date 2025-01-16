from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from google._upb._message import RepeatedScalarContainer, RepeatedCompositeContainer
from typing_extensions import Any

from a7p import profedit_pb2, A7PFactory
from a7p.factory import Switches
from a7p.logger import color_fmt, logger


@dataclass
class RecoverResult:
    recovered: bool
    path: Path | str
    old_value: str | None = None
    new_value: Any = None

    def print(self):

        if isinstance(self.path, Path):
            path_string = f"{self.path.as_posix()}"
        else:
            path_string = f"{self.path}"

        if len(path_string) > 30:
            path_string = path_string[:27] + "..."
        path_string = path_string.ljust(30)

        if self.recovered:
            prefix = color_fmt("Recovered".ljust(10), levelname="INFO")
        else:
            prefix = color_fmt("Skipped".ljust(10), levelname="WARNING")

        def truncate_list(_value: Any) -> str:
            if isinstance(_value, (RepeatedScalarContainer, RepeatedCompositeContainer, list, tuple)):
                _value = [str(v) for v in _value]
                if len(_value) > 6:
                    _value = f'[ {", ".join(_value[:3])}, ... {", ".join(_value[-3:])} ]'
                else:
                    _value = f'[ {",".join(_value)} ]'
            return _value

        def truncate(string: str):
            string = str(string).replace("\n", " ")
            if len(string) > 50:
                # string = f'[ {string[:25]} ... {string[-25:]} ]'
                string = f'{string[:25]} ... {string[-25:]}'
            return string

        old_value = str(truncate_list(self.old_value))
        new_value = str(truncate_list(self.new_value))

        print(f"{prefix} : {path_string} : value : {truncate(old_value)} -> {truncate(new_value)}")


class Recover:
    def __init__(self):
        self.recover_funcs = {}

    def register(self, path, func):
        raise NotImplementedError("register not implemented as is abstract method")

    @staticmethod
    def split_path(path: Path | str) -> list:
        raise NotImplementedError("split_path not implemented as is abstract method")

    @classmethod
    def get_value_by_violation(cls, payload, violation):
        # raise NotImplementedError("get_value_by_violation not implemented as is abstract method")
        _value = payload
        # _path = violation.path.split('.')
        _path = cls.split_path(violation.path)
        for p in _path:
            if hasattr(_value, p):
                _value = getattr(_value, p)

        return deepcopy(_value)

    def recover_one(self, payload, violation):

        if violation.path in self.recover_funcs:
            old_value = self.get_value_by_violation(payload, violation)
            self.recover_funcs[violation.path](payload)
            new_value = self.get_value_by_violation(payload, violation)
            return RecoverResult(True, violation.path, old_value, new_value)

        return RecoverResult(False, violation.path, None, None)

    def recover(self, payload, violations):
        results = []
        for v in violations:
            result = self.recover_one(payload, v)
            results.append(result)
        return results


def fix_str_len_type(string: str, expected_len: int, default: str = "nil"):
    if isinstance(string, str):
        return string[:expected_len]
    return default[:expected_len]


def _recover_proto_bullet_name(payload):
    payload.profile.bullet_name = fix_str_len_type(payload.profile.bullet_name, 50)


def _recover_proto_cartridge_name(payload):
    payload.profile.cartridge_name = fix_str_len_type(payload.profile.cartridge_name, 50)


def _recover_proto_profile_name(payload):
    payload.profile.profile_name = fix_str_len_type(payload.profile.profile_name, 50)


def _recover_proto_user_note(payload):
    payload.profile.user_note = fix_str_len_type(payload.profile.user_note, 250,
                                                 "Warning: Restored profile")


def _recover_proto_short_name_top(payload):
    payload.profile.short_name_top = fix_str_len_type(payload.profile.short_name_top, 8)


def _recover_proto_short_name_bot(payload):
    payload.profile.short_name_bot = fix_str_len_type(payload.profile.short_name_bot, 8)


def _recover_proto_zero_x(payload):
    payload.profile.zero_x = 0


def _recover_proto_zero_y(payload):
    payload.profile.zero_y = 0


def _recover_proto_sc_height(payload):
    payload.profile.sc_height = 90


def _recover_proto_r_twist(payload):
    payload.profile.r_twist = 10


def _recover_proto_c_muzzle_velocity(payload):
    payload.profile.c_muzzle_velocity = 8000


def _recover_proto_c_zero_temperature(payload):
    payload.profile.c_zero_temperature = 15


def _recover_proto_c_t_coeff(payload):
    payload.profile.c_t_coeff = 1000


def _recover_proto_c_zero_distance_idx(payload):
    payload.profile.c_zero_distance_idx = 0


def _recover_proto_c_zero_air_temperature(payload):
    payload.profile.c_zero_air_temperature = 15


def _recover_proto_c_zero_air_pressure(payload):
    payload.profile.c_zero_air_pressure = 10000


def _recover_proto_c_zero_air_humidity(payload):
    payload.profile.c_zero_air_pressure = 0


def _recover_proto_c_zero_w_pitch(payload):
    payload.profile.c_zero_w_pitch = 0


def _recover_proto_c_zero_p_temperature(payload):
    payload.profile.c_zero_p_temperature = 15


def _recover_proto_b_diameter(payload):
    payload.profile.b_diameter = 338


def _recover_proto_b_weight(payload):
    payload.profile.b_weight = 3000


def _recover_proto_b_length(payload):
    payload.profile.b_length = 1700


def _recover_proto_twist_dir(payload):
    payload.twist_dir = profedit_pb2.TwistDir.RIGHT


def _recover_proto_bc_type(payload):
    logger.warning("Drag model restored to G7")
    payload.bc_type = profedit_pb2.GType.G7


def _recover_proto_switches(payload):
    del payload.profile.switches[:]
    payload.profile.switches.extend(Switches())


def _recover_proto_coef_rows(payload):
    logger.warning("Drag model coefficients restored to 0.1")
    del payload.profile.coef_rows[:]
    payload.profile.coef_rows.extend(
        profedit_pb2.CoefRow(
            bc_cd=round(0.1 * 10000),
            mv=round(0 * 10)
        )
    )


def _recover_proto_distances(payload):
    del payload.profile.distances[:]
    payload.profile.distances[:] = [int(d * 100) for d in A7PFactory.DistanceTable.LONG_RANGE.value]


def _recover_proto_caliber(payload):
    payload.profile.caliber = fix_str_len_type(payload.profile.caliber, 50)


def _recover_proto_device_uuid(payload):
    payload.profile.device_uuid = fix_str_len_type(payload.profile.device_uuid, 50, "")


class RecoverProto(Recover):

    def register(self, path, func):
        self.recover_funcs[path] = func

    @staticmethod
    def split_path(path: Path | str) -> list:
        return path.split('.')


recover_proto = RecoverProto()

recover_proto.register("profile.profile_name", _recover_proto_short_name_top)
recover_proto.register("profile.cartridge_name", _recover_proto_cartridge_name)
recover_proto.register("profile.bullet_name", _recover_proto_bullet_name)
recover_proto.register("profile.user_note", _recover_proto_user_note)

recover_proto.register("profile.short_name_top", _recover_proto_short_name_top)
recover_proto.register("profile.short_name_bot", _recover_proto_short_name_bot)

recover_proto.register("profile.zero_x", _recover_proto_zero_x)
recover_proto.register("profile.zero_y", _recover_proto_zero_y)

recover_proto.register("profile.sc_height", _recover_proto_sc_height)
recover_proto.register("profile.r_twist", _recover_proto_r_twist)

recover_proto.register("profile.c_muzzle_velocity", _recover_proto_c_muzzle_velocity)
recover_proto.register("profile.c_zero_temperature", _recover_proto_c_zero_temperature)
recover_proto.register("profile.c_t_coeff", _recover_proto_c_t_coeff)
recover_proto.register("profile.c_zero_distance_idx", _recover_proto_c_zero_distance_idx)
recover_proto.register("profile.c_zero_air_temperature", _recover_proto_c_zero_air_temperature)
recover_proto.register("profile.c_zero_air_pressure", _recover_proto_c_zero_air_pressure)
recover_proto.register("profile.c_zero_air_humidity", _recover_proto_c_zero_air_humidity)
recover_proto.register("profile.c_zero_w_pitch", _recover_proto_c_zero_w_pitch)
recover_proto.register("profile.c_zero_p_temperature", _recover_proto_c_zero_p_temperature)

recover_proto.register("profile.b_diameter", _recover_proto_b_diameter)
recover_proto.register("profile.b_weight", _recover_proto_b_weight)
recover_proto.register("profile.b_length", _recover_proto_b_length)

recover_proto.register("profile.twist_dir", _recover_proto_twist_dir)
recover_proto.register("profile.bc_type", _recover_proto_bc_type)

recover_proto.register("profile.switches", _recover_proto_switches)
recover_proto.register("profile.distances", _recover_proto_distances)
recover_proto.register("profile.coef_rows", _recover_proto_coef_rows)
recover_proto.register("profile.caliber", _recover_proto_caliber)
recover_proto.register("profile.device_uuid", _recover_proto_device_uuid)


class RecoverSpec(Recover):

    def register(self, path, func):
        self.recover_funcs[Path(path)] = func

    @staticmethod
    def split_path(path: Path | str) -> list:
        return Path(path).as_posix().split("/")[1:]


def _recover_spec_bullet_name(payload):
    payload.profile.bullet_name = fix_str_len_type(payload.profile.bullet_name, 49)


def _recover_spec_cartridge_name(payload):
    payload.profile.cartridge_name = fix_str_len_type(payload.profile.cartridge_name, 49)


def _recover_spec_caliber(payload):
    payload.profile.caliber = fix_str_len_type(payload.profile.caliber, 49)


def _recover_spec_profile_name(payload):
    payload.profile.profile_name = fix_str_len_type(payload.profile.profile_name, 49)


def _recover_spec_uuid(payload):
    payload.profile.device_uuid = fix_str_len_type(payload.profile.device_uuid, 49)


def _recover_spec_user_note(payload):
    payload.profile.user_note = fix_str_len_type(payload.profile.user_note, 1023,
                                                 "Warning: Restored profile")


def _recover_spec_short_name_top(payload):
    payload.profile.short_name_top = fix_str_len_type(payload.profile.short_name_top, 7)


def _recover_spec_short_name_bot(payload):
    payload.profile.short_name_bot = fix_str_len_type(payload.profile.short_name_bot, 7)


def _recover_spec_zero_x(payload):
    payload.profile.zero_x = 0


def _recover_spec_zero_y(payload):
    payload.profile.zero_y = 0


def _recover_spec_sc_height(payload):
    payload.profile.sc_height = 90


def _recover_spec_r_twist(payload):
    payload.profile.r_twist = 10


def _recover_spec_c_muzzle_velocity(payload):
    payload.profile.c_muzzle_velocity = 8000


def _recover_spec_c_zero_temperature(payload):
    payload.profile.c_zero_temperature = 15


def _recover_spec_c_t_coeff(payload):
    payload.profile.c_t_coeff = 1000


def _recover_spec_c_zero_distance_idx(payload):
    payload.profile.c_zero_distance_idx = 0


def _recover_spec_c_zero_air_temperature(payload):
    payload.profile.c_zero_air_temperature = 15


def _recover_spec_c_zero_air_pressure(payload):
    payload.profile.c_zero_air_pressure = 10000


def _recover_spec_c_zero_air_humidity(payload):
    payload.profile.c_zero_air_pressure = 0


def _recover_spec_c_zero_w_pitch(payload):
    payload.profile.c_zero_w_pitch = 0


def _recover_spec_c_zero_p_temperature(payload):
    payload.profile.c_zero_p_temperature = 15


def _recover_spec_b_diameter(payload):
    payload.profile.b_diameter = 338


def _recover_spec_b_weight(payload):
    payload.profile.b_weight = 3000


def _recover_spec_b_length(payload):
    payload.profile.b_length = 1700


def _recover_spec_twist_dir(payload):
    payload.twist_dir = profedit_pb2.TwistDir.RIGHT


def _recover_spec_bc_type(payload):
    logger.warning("Drag model restored to G7")
    payload.bc_type = profedit_pb2.GType.G7


def _recover_spec_switches(payload):
    del payload.profile.switches[:]
    payload.profile.switches.extend(Switches())


def _recover_spec_coef_rows(payload):
    logger.warning("Drag model coefficients restored to 0.1")
    del payload.profile.coef_rows[:]
    payload.profile.coef_rows.extend(
        profedit_pb2.CoefRow(
            bc_cd=round(0.1 * 10000),
            mv=round(0 * 10)
        )
    )


def _recover_spec_distances(payload):
    del payload.profile.distances[:]
    payload.profile.distances[:] = [int(d * 100) for d in A7PFactory.DistanceTable.LONG_RANGE.value]


recover_spec = RecoverSpec()

recover_spec.register("~/profile/profile_name", _recover_spec_profile_name)
recover_spec.register("~/profile/cartridge_name", _recover_spec_cartridge_name)
recover_spec.register("~/profile/bullet_name", _recover_spec_bullet_name)
recover_spec.register("~/profile/user_note", _recover_spec_user_note)
recover_spec.register("~/profile/device_uuid", _recover_spec_uuid)
recover_spec.register("~/profile/short_name_top", _recover_spec_short_name_top)
recover_spec.register("~/profile/short_name_bot", _recover_spec_short_name_bot)

recover_spec.register("~/profile/zero_x", _recover_spec_zero_x)
recover_spec.register("~/profile/zero_y", _recover_spec_zero_y)

recover_spec.register("~/profile/sc_height", _recover_spec_sc_height)
recover_spec.register("~/profile/r_twist", _recover_spec_r_twist)

recover_spec.register("~/profile/c_muzzle_velocity", _recover_spec_c_muzzle_velocity)
recover_spec.register("~/profile/c_zero_temperature", _recover_spec_c_zero_temperature)
recover_spec.register("~/profile/c_t_coeff", _recover_spec_c_t_coeff)
recover_spec.register("~/profile/c_zero_distance_idx", _recover_spec_c_zero_distance_idx)
recover_spec.register("~/profile/c_zero_air_temperature", _recover_spec_c_zero_air_temperature)
recover_spec.register("~/profile/c_zero_air_pressure", _recover_spec_c_zero_air_pressure)
recover_spec.register("~/profile/c_zero_air_humidity", _recover_spec_c_zero_air_humidity)
recover_spec.register("~/profile/c_zero_w_pitch", _recover_spec_c_zero_w_pitch)
recover_spec.register("~/profile/c_zero_p_temperature", _recover_spec_c_zero_p_temperature)

recover_spec.register("~/profile/b_diameter", _recover_spec_b_diameter)
recover_spec.register("~/profile/b_weight", _recover_spec_b_weight)
recover_spec.register("~/profile/b_length", _recover_spec_b_length)

recover_spec.register("~/profile/twist_dir", _recover_spec_twist_dir)
recover_spec.register("~/profile/bc_type", _recover_spec_bc_type)

recover_spec.register("~/profile/distances", _recover_spec_distances)
recover_spec.register("~/profile/switches", _recover_spec_switches)
recover_spec.register("~/profile/coef_rows", _recover_spec_coef_rows)
