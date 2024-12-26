import a7p
from a7p import exceptions, pydantic, recover
from a7p.logger import color_print

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
            data['profile']['c_zero_distance_idx'] = 2
            try:
                pydantic.validate(data)
            except exceptions.A7PValidationError as err:
                for v in err.violations:
                    color_print(v.format(), levelname="WARNING")

                data = a7p.to_dict(err.payload)

                results = pydantic.recover(data, err.violations)
                for r in results:
                    r.print()
                color_print("Final validation", levelname="INFO")
                try:
                    pydantic.validate(data)
                except exceptions.A7PValidationError as err:
                    for v in err.violations:
                        color_print(v.format(), levelname="WARNING")
