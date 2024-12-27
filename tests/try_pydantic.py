import a7p
from a7p import exceptions, pydantic
from a7p.logger import color_print

if __name__ == "__main__":
    with open("broken.a7p", 'rb') as fp:
        payload = a7p.load(fp, validate_=False)

        try:
            pydantic.validate(payload)
        except exceptions.A7PValidationError as err:
            for v in err.violations:
                color_print(v.format(), levelname="WARNING")

            print()
            try:
                restored_payload = pydantic.validate(payload, restore=True)
            except exceptions.A7PValidationError as err:
                for v in err.violations:
                    color_print(v.format(), levelname="WARNING")
