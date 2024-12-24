from google._upb._message import RepeatedScalarContainer, RepeatedCompositeContainer
from pydantic import ValidationError

import a7p
from a7p import profedit_pb2, exceptions
from .models import Payload
from .template import PAYLOAD_TEMPLATE
from ..exceptions import A7PValidationError


def get_dict_field(payload: dict, field_path):
    loc = field_path.split('.')
    current = payload

    for part in loc:
        if part.isdigit():  # If part is a number (array index)
            current = current[int(part)]  # Access list by index
        else:
            current = current.get(part)  # Access dict by key (assuming proto_obj is a dict)

        if current is None:  # If the field doesn't exist
            raise KeyError(f"Field not found: {field_path}")

    return current  # Return the final value


def get_payload_field(payload: Payload, field_path):
    loc = field_path.split('.')
    current = payload

    for part in loc:
        if part.isdigit():  # If part is a number (array index)
            current = current[int(part)]  # Access list by index
        else:
            current = getattr(current, part)  # Access dict by key (assuming proto_obj is a dict)

        if current is None:  # If the field doesn't exist
            raise AttributeError(f"Field not found: {field_path}")

    return current  # Return the final value


def set_dict_field(payload: dict, field_path, value):
    loc = field_path.split('.')  # Split path into components
    current = payload

    # Traverse the path until the second-to-last part
    for part in loc[:-1]:
        if part.isdigit():  # If part is a number (array index)
            current = current[int(part)]  # Access list element by index
        else:
            current = current.get(part)  # Access field using attribute name

        if current is None:
            raise KeyError(f"Field not found: {field_path}")

    # Now we're at the last part, set the value
    last_part = loc[-1]
    if last_part.isdigit():  # If the last part is a number (array index)
        current[int(last_part)] = value  # Set the list element at that index
    else:
        current[last_part] = value


def set_payload_field(payload: profedit_pb2.Payload, field_path, value):
    loc = field_path.split('.')  # Split path into components
    current = payload

    # Traverse the path until the second-to-last part
    for part in loc[:-1]:
        if part.isdigit():  # If part is a number (array index)
            current = current[int(part)]  # Access list element by index
        else:
            current = getattr(current, part)  # Access field using attribute name

        if current is None:
            raise AttributeError(f"Field not found: {field_path}")

    # Now we're at the last part, set the value
    last_part = loc[-1]
    if last_part.isdigit():  # If the last part is a number (array index)
        current[int(last_part)] = value  # Set the list element at that index
    else:

        field = getattr(current, last_part)
        if isinstance(field, RepeatedScalarContainer):
            # del field[:]
            field[:] = value
        elif isinstance(field, RepeatedCompositeContainer):
            # del field[:]
            print("composite", field)
            del field[:]
            field.extend(value)
        else:
            setattr(current, last_part, value)  # Set the field value using setattr


def validate(data: dict):
    try:
        Payload.model_validate(data)
    except ValidationError as err:
        print()
        print("Pydantic validation error")
        violations = []
        for error in err.errors():
            # print(error)
            field_path = '.'.join(map(str, error.get('loc', tuple())))
            violations.append(
                exceptions.Violation(
                    path=field_path,
                    value=error.get('input', None),
                    reason=error.get('msg', "Undefined error")
                )
            )
        raise A7PValidationError(
            "Pydantic validation error",
            payload=a7p.from_dict(data),
            violations=violations
        )


def recover(data: dict, violations: list[exceptions.Violation]):
    for violation in violations:
        path = violation.path
        old_value = get_dict_field(data, path)
        try:
            new_value = get_dict_field(PAYLOAD_TEMPLATE, path)
        except KeyError:
            print("Not recovered", path, old_value)
        else:
            set_dict_field(data, path, new_value)
            print("Recovered", path, old_value, new_value)
    # print("pre", get_dict_field(data, "profile.c_muzzle_velocity"))
    # set_dict_field(data, "profile.c_muzzle_velocity", 8000)
    # print("post", get_dict_field(data, "profile.c_muzzle_velocity"))
    # print()
    # print("pre", get_dict_field(data, "profile.distances.0"))
    # set_dict_field(data, "profile.distances.0", 123456)
    # print("post", get_dict_field(data, "profile.distances.0"))
    # print()
    # print("pre", get_dict_field(data, "profile.distances"))
    # set_dict_field(data, "profile.distances", [10000, 20000])
    # set_dict_field(data, "profile.distances", [10000, 20000, 30000])
    # print("post", get_dict_field(data, "profile.distances"))
    # print()
    # print("pre", get_dict_field(data, "profile.switches"))
    # set_dict_field(data, "profile.switches", [{'c_idx': 1}, {'c_idx': 1}])
    # print("post", get_dict_field(data, "profile.switches"))
    # print()
    # print("pre", get_dict_field(data, "profile.switches.0"))
    # set_dict_field(data, "profile.switches.0", {'c_idx': 5})
    # print("post", get_dict_field(data, "profile.switches.0"))
    # print()
    #
    # print("pre", get_dict_field(data, "profile.switches.0.c_idx"))
    # set_dict_field(data, "profile.switches.0.c_idx", 3)
    # print("post", get_dict_field(data, "profile.switches.0.c_idx"))
    # print()
    #
    # print(a7p.from_dict(data))
