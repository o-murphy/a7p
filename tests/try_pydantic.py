from google.protobuf.json_format import MessageToDict
from pydantic import ValidationError

import a7p
from a7p.exceptions import A7PValidationError
from a7p.pydantic import Payload

if __name__ == "__main__":
    from pprint import pprint


    def set_value_by_field_path(payload, field_path, value):
        """
        Sets a value in a nested protobuf message based on a field path.

        Args:
            payload: The protobuf message object.
            field_path: The path to the field (can be a string or a list of field names).
            value: The value to set.
        """
        # Convert string path to list if it's a string
        if isinstance(field_path, str):
            field_path = field_path.split('.')

        # Traverse the message to the second-to-last field in the path
        attr = payload
        for field in field_path[:-1]:
            if hasattr(attr, field):
                attr = getattr(attr, field)
            else:
                raise AttributeError(f"Field '{field}' not found in {attr.__class__.__name__}")

        # Set the value at the last field in the path
        last_field = field_path[-1]
        if hasattr(attr, last_field):
            setattr(attr, last_field, value)
        else:
            raise AttributeError(f"Field '{last_field}' not found in {attr.__class__.__name__}")


    with open("broken.a7p", 'rb') as fp:
        try:
            payload = a7p.load(fp, validate_=True)
        except A7PValidationError as err:
            for v in err.all_violations:
                print(v.format())
            payload = err.payload
        finally:
            payload.profile.distances[:] = [100000000]
            data = MessageToDict(
                payload,
                including_default_value_fields=True,
                preserving_proto_field_name=True
            )
            print("Pydantic validation there")
            data['profile']['bc_type'] = 'CUSTOM'
            data['profile']['sc_height'] = 'invalid'
            try:
                Payload.model_validate(data)
            except ValidationError as err:
                print("Errors", len(err.errors()))
                for e in err.errors():
                    pprint(e)

                #     # attr = payload
                #     # for key in e['loc']:
                #     #     if isinstance(key, str):
                #     #         attr = getattr(attr, key)
                #     #     elif isinstance(key, int):
                #     #         attr = attr[key]
                #
                #     field_path = e['loc']
                #     if isinstance(e['loc'][-1], int):
                #         field_path = e['loc'][:-1]
                #
                #     last_key = field_path[-1]
                #     if last_key == 'c_muzzle_velocity':
                #         set_value_by_field_path(payload, ".".join([str(i) for i in e['loc']]), 8000)
                #     if last_key == 'distance':
                #         set_value_by_field_path(payload, ".".join([str(i) for i in e['loc']]), [1000])
                #     else:
                #         print(e['loc'])
                #
                # data = MessageToDict(
                #     payload,
                #     including_default_value_fields=True,
                #     preserving_proto_field_name=True
                # )
                # print(data['profile']['distances'])
                # try:
                #     Payload.model_validate(data)
                # except ValidationError as err:
                #     print("Errors", len(err.errors()))
                #     for e in err.errors():
                #         pprint(e)
