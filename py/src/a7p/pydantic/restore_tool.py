import argparse
import logging
from pathlib import Path

import a7p
from a7p import pydantic
from a7p.logger import color_print

parser = argparse.ArgumentParser(
    prog='a7p-recover'
)

parser.add_argument("path", help="Path to broken .a7p file", type=Path)

logger = logging.getLogger('a7p')
logger.setLevel(logging.DEBUG)


def main():
    args = parser.parse_args()
    file_path: Path = args.path
    if not file_path.exists():
        parser.error(f"No such file or directory: '{file_path}'")

    with open(file_path.absolute(), 'rb') as fp:
        payload = a7p.load(fp, validate_=False)

        model, restored, violations = pydantic.validate(payload)
        for v in violations:
            color_print(v.format(), levelname="WARNING")

        if violations:
            logger.info("Started restore process")
            model, restored, violations = pydantic.validate(payload, restore=True)
            for r in restored:
                r.print()

            if violations:
                for v in violations:
                    color_print(v.format(), levelname="WARNING")
            else:
                dump = model.model_dump(mode="json")

                with open(file_path.with_stem(file_path.stem + "_restored"), 'wb') as fp:
                    restored_payload = a7p.from_dict(dump)
                    a7p.dump(restored_payload, fp)
p

if __name__ == "__main__":
    main()
