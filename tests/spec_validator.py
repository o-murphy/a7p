from a7p import exceptions, load, logger, validate
from a7p.fixtool import protofix, specfix

if __name__ == '__main__':

    with open("broken.a7p", "rb") as fp:
        try:
            # trying to load file data to payload
            payload = load(fp, fail_fast=False)
        except exceptions.A7PValidationError as e:
            for v in e.all_violations:
                logger.color_print(v.format())

            # trying to fix payload by spec
            specfix.fix(e.payload, e.spec_violations)

            try:
                # trying to validate fixed payload
                validate(e.payload, fail_fast=True)
            except exceptions.A7PValidationError as e:

                # if still got proto violations trying to fix them too
                protofix.fix(e.payload, e.proto_violations)

                try:
                    # last validation for get fix results
                    validate(e.payload, fail_fast=False)
                except exceptions.A7PValidationError as e:

                    for v in e.all_violations:
                        logger.color_print(v.format())



