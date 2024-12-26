from functools import wraps


def field_validator(
        field: str,
        /,
        *fields: str, ):
    """
    A decorator to mark methods for field validation or other field-specific behaviors.
    """

    def decorator(func):
        func._validator = True
        func._fields = field, *fields  # Attach metadata to the function
        return func

    return decorator


def field_recovery(
        field: str,
        /,
        *fields: str, ):
    """
    A decorator to mark methods for field validation or other field-specific behaviors.
    """

    def decorator(func):
        func._recovery = True
        func._fields = field, *fields  # Attach metadata to the function
        return func

    return decorator


class RecoveryFieldRegistryMeta(type):
    """
    Metaclass to register all methods decorated with @custom_field_decorator.
    """

    def __new__(cls, name, bases, dct):
        # Create the class
        klass = super().__new__(cls, name, bases, dct)

        # Initialize the registry
        klass._fields_registry = {}
        klass._validators_registry = {}
        klass._recovery_registry = {}

        # Register annotated fields
        if "__annotations__" in dct:

            for field_name, field_type in dct["__annotations__"].items():
                # if hasattr(field_type, "ge") or hasattr(field_type, "le"):
                klass._fields_registry[field_name] = field_type
                print(f"Registered field: {field_name} with validator: {field_type}")


        # Register decorated methods
        for attr_name, attr_value in dct.items():
            if hasattr(attr_value, "_fields"):  # Check if the method has the field_name metadata
                if isinstance(attr_value, classmethod):  # Check if it's a classmethod
                    fields = attr_value._fields
                    # Register it as a classmethod in v
                    for field in fields:
                        if field not in klass._fields_registry:
                            raise AttributeError(
                                f"Cannot register method {attr_name} without field {field}")

                        if hasattr(attr_value, "_validator"):
                            klass._validators_registry[field] = attr_value
                        if hasattr(attr_value, "_recovery"):
                            klass._recovery_registry[field] = attr_value
                    print(f"Registered {attr_name} as classmethod for {fields} in {name}")
                elif callable(attr_value):  # If it's a regular method (not classmethod)
                    fields = attr_value._fields
                    # Register it as a normal method in v
                    for field in fields:
                        if field not in klass._fields_registry:
                            raise AttributeError(
                                f"Cannot register method {attr_name} without field {field}")
                        if hasattr(attr_value, "_validator"):
                            klass._validators_registry[field] = attr_value
                        if hasattr(attr_value, "_recovery"):
                            klass._recovery_registry[field] = attr_value
                    print(f"Registered {attr_name} for {fields} in {name}")

        return klass


class BaseValidatorModel(metaclass=RecoveryFieldRegistryMeta):

    @classmethod
    def validate(cls, data: dict, recover=False):
        errors = {}

        for field_name, convention in cls._fields_registry.items():
            if field_name in data:
                field_value = data[field_name]
                if field_name in cls._validators_registry:
                    field_validator = cls._validators_registry[field_name]
                    if isinstance(field_validator, classmethod):
                        if not field_validator.__func__(cls, field_value, data):
                            errors[field_name] = "error"
                    elif callable(field_validator):
                        if not field_validator(cls, field_value, data):
                            errors[field_name] = "error"
                if callable(convention):
                    convention_result = convention(field_value)
                    print("c", convention_result)
                    if isinstance(convention_result, bool):
                        if not convention_result:
                            errors[field_name] = "error"
                    else:
                        field_value = convention_result

                if errors.get(field_name, None) and recover:
                    recover_func = cls._recovery_registry.get(field_name, None)
                    if isinstance(recover_func, classmethod):
                        field_value = recover_func.__func__(cls, field_value, data)
                    elif callable(recover_func):
                        field_value = recover_func(cls, field_value, data)
                data[field_name] = field_value
        return data, errors

def assert_type(*expected_types):

    if not all(isinstance(t, type) for t in expected_types):
        raise ValueError("all expected_types must be valid types.")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if args:
                first_arg = args[0]
                if not isinstance(first_arg, tuple(expected_types)):
                    # raise TypeError
                    # return lambda *args, **kwargs: False
                    return False
            return func(*args, **kwargs)

        return wrapper

    return decorator


def varint(ge=None, le=None):

    @assert_type(int)
    def validator(value):
        if ge is not None and value < ge:
            return False
        if le is not None and value > le:
            return False
        return True
    validator.ge = ge
    validator.le = le
    return validator

def restore(validator, default=0):
    def wrapper(value, *args, **kwargs):
        if validator(value, *args, **kwargs):
            return value
        return default
    return wrapper

class ViolationsRecovery(BaseValidatorModel):

    index0: restore(varint(1, 5), 3)
    index1: varint(1, 5)

    @field_validator("index1", "index0")
    @classmethod
    def validate_index(cls, value, data: dict):
        # print(f"Validating index with value: {value}")
        # if value < 0:
        #     raise ValueError("index must be non-negative")
        return value

    @field_recovery("index1")
    @classmethod
    def recover_index(cls, value, data: dict):
        return restore(varint(1, 5), default=0)(value)

recovered_data, errors = ViolationsRecovery.validate({"index1": 100, "index2": 'abc'})
print(recovered_data, errors)

recovered_data, errors = ViolationsRecovery.validate({"index1": 100, "index2": 'abc'}, recover=True)
print(recovered_data, errors)