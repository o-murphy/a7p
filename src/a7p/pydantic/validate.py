from typing import Any

from pydantic import ValidationError
from typing_extensions import List, Dict

import a7p
from a7p import exceptions, profedit_pb2
from a7p.pydantic.models import Payload
from a7p.pydantic.template import PAYLOAD_RECOVERY_SCHEMA


def get_dict_field(payload_dict: Dict[str, Any], field_path: str):
    loc = field_path.split('.')
    current = payload_dict

    for part in loc:
        if part.isdigit():  # If part is a number (array index)
            current = current[int(part)]  # Access list by index
        else:
            current = current.get(part)  # Access dict by key (assuming proto_obj is a dict)

        if current is None:  # If the field doesn't exist
            raise KeyError(f"Field not found: %s" % field_path)

    return current  # Return the final value


def set_dict_field(payload_dict: Dict[str, Any], field_path: str, value: Any):
    loc = field_path.split('.')  # Split path into components
    current = payload_dict

    # Traverse the path until the second-to-last part
    for part in loc[:-1]:
        if part.isdigit():  # If part is a number (array index)
            current = current[int(part)]  # Access list element by index
        else:
            current = current.get(part)  # Access field using attribute name

        if current is None:
            raise KeyError(f"Field not found: %s" % field_path)

    # Now we're at the last part, set the value
    last_part = loc[-1]
    if last_part.isdigit():  # If the last part is a number (array index)
        current[int(last_part)] = value  # Set the list element at that index
    else:
        current[last_part] = value


def validate(payload: profedit_pb2.Payload, restore=False):
    payload_dict = a7p.to_dict(payload)
    context = {
        "restore": restore,
        "restored": []
    }
    model = None
    violations = []

    try:
        model = Payload.model_validate(payload_dict, context=context)
    except ValidationError as err:
        for error in err.errors():
            field_path = '.'.join(map(str, error.get('loc', tuple())))
            violations.append(
                exceptions.Violation(
                    path=field_path,
                    value=error.get('input', None),
                    reason=error.get('msg', "Undefined error")
                )
            )
        # raise exceptions.A7PValidationError(
        #     "Pydantic validation error",
        #     payload=a7p.from_dict(payload_dict),
        #     violations=violations
        # )
        return model, context.get("restored"), violations
    return model, context.get("restored"), violations


def recursive_recover(path: str, old_value: Any) -> Any:
    loc = path.split('.') if path else []
    recover_value = get_dict_field(PAYLOAD_RECOVERY_SCHEMA, path)

    if callable(recover_value):
        return recover_value(old_value)
    elif isinstance(recover_value, dict):
        return {k: recursive_recover(".".join(loc + [k]), None) for k in recover_value}
    elif isinstance(recover_value, list):
        return [recursive_recover(".".join(loc + [str(i)]), None) for i in range(len(recover_value))]
    return recover_value


def recover(payload_dict: Dict[str, Any], violations: List[exceptions.Violation]):
    try:
        Payload.model_validate(payload_dict, context={"recovery": PAYLOAD_RECOVERY_SCHEMA})
    except ValidationError as err:
        violations = []
        for error in err.errors():
            field_path = '.'.join(map(str, error.get('loc', tuple())))
            violations.append(
                exceptions.Violation(
                    path=field_path,
                    value=error.get('input', None),
                    reason=error.get('msg', "Undefined error")
                )
            )
        raise exceptions.A7PValidationError(
            "Pydantic validation error",
            payload=a7p.from_dict(payload_dict),
            violations=violations
        )

    # results: List[RecoverResult] = []
    #
    # for violation in violations:
    #     path = violation.path
    #     try:
    #         old_value = get_dict_field(payload_dict, path)
    #
    #         try:
    #             new_value = recursive_recover(path, old_value)
    #             set_dict_field(payload_dict, path, new_value)
    #             results.append(RecoverResult(
    #                 recovered=True,
    #                 path=path,
    #                 old_value=old_value,
    #                 new_value=new_value,
    #             ))
    #         except (KeyError, ValueError, AttributeError) as e:
    #             # Log the error if needed
    #             results.append(RecoverResult(
    #                 recovered=False,
    #                 path=path,
    #                 old_value=old_value,
    #                 new_value=None,
    #             ))
    #     except KeyError as e:
    #         # Log missing keys
    #         results.append(RecoverResult(
    #             recovered=False,
    #             path=path,
    #             old_value=None,
    #             new_value=None,
    #         ))
    #
    # return results
