from a7p import exceptions, validate
from a7p.exceptions import A7PValidationError, Violation
from a7p.recover import recover_spec, recover_proto, RecoverResult
from a7p.logger import color_print, logger, color_fmt


def _print_recover_results_count(violations: list[Violation], results: list[RecoverResult]):
    total = len(violations)
    recovered = sum(1 for r in results if r.recovered)
    strings = [
        color_fmt(f"Total: {total}"),
        color_fmt(f"Recovered: {recovered}", levelname="INFO"),
        color_fmt(f"Skipped: {total - recovered}", levelname="WARNING"),
    ]
    prefix = "RESULT".ljust(10)
    print(f'{color_fmt(prefix, levelname="LIGHT_BLUE")} : {", ".join(strings)}')


def attempt_to_recover(validation_error: A7PValidationError):
    logger.info("Attempting to recover payload")

    # trying to fix payload by spec
    logger.info("Attempting to recover by spec violations")
    results = recover_spec.recover(validation_error.payload, validation_error.spec_violations)

    for r in results:
        r.print()
    _print_recover_results_count(validation_error.spec_violations, results)

    try:
        # trying to validate fixed payload
        validate(validation_error.payload, fail_fast=True)
    except exceptions.A7PValidationError as err:

        # if still got proto violations trying to fix them too
        logger.info("Attempting to recover by proto violations")
        results = recover_proto.recover(err.payload, err.proto_violations)

        for r in results:
            r.print()
        _print_recover_results_count(err.proto_violations, results)

        try:
            # last validation for get fix results
            logger.info("Final validation")
            validate(err.payload, fail_fast=False)
        except exceptions.A7PValidationError as err:
            for v in err.all_violations:
                color_print(v.format(), levelname="WARNING")
            logger.warning("Violations still found")
            logger.error("Can't recover the payload")
            return err
        else:
            logger.info("No violations found")
            logger.info("Payload completely recovered")

    return None
