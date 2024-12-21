from a7p import exceptions, load, logger, validate

if __name__ == '__main__':

    with open("broken.a7p", "rb") as fp:
        try:
            payload = load(fp, True, fail_fast=False)
        except exceptions.A7PValidationError as e:
            for v in e.all_violations:
                logger.color_print(v.format())

            print()
            try:
                validate(e.payload, fail_fast=True)
            except exceptions.A7PValidationError as e:
                for v in e.all_violations:
                    logger.color_print(v.format())
