from a7p import exceptions, load
from a7p.logger import color_print, logger
from a7p.recover.recover_process import attempt_to_recover


def _example():
    try:
        with open("broken.a7p", "rb") as fp:
            try:
                # trying to load file data to payload
                load(fp, fail_fast=False)
            except exceptions.A7PValidationError as err:
                color_print("Violations found:", levelname="ERROR")
                for v in err.all_violations:
                    color_print(v.format(), levelname="WARNING")
                attempt_to_recover(err)
            else:
                logger.info("No violations found")

    except IOError as e:
        print("Error: %s" % e)

if __name__ == '__main__':
    _example()




