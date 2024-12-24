import a7p
from a7p import exceptions, pydantic

if __name__ == "__main__":
    with open("broken.a7p", 'rb') as fp:
        try:
            payload = a7p.load(fp, validate_=True)
        except exceptions.A7PValidationError as err:
            # for v in err.all_violations:
            #     print(v.format())
            payload = err.payload
            del payload.profile.distances[:]
        finally:
            data = a7p.to_dict(payload)
            try:
                pydantic.validate(data)
            except exceptions.A7PValidationError as err:
                for v in err.violations:
                    print(v.format())
                data = a7p.to_dict(err.payload)
                pydantic.recover(data, err.violations)

                print()
                print("Final validation")
                try:
                    pydantic.validate(data)
                except exceptions.A7PValidationError as err:
                    for v in err.violations:
                        print(v.format())
