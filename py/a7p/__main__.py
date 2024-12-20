import asyncio
import pathlib
import sys
from argparse import ArgumentParser
from asyncio import Semaphore
from dataclasses import dataclass
from importlib import metadata

from a7p import A7PFile, A7PDataError, A7PError, A7PValidationError
from a7p import protovalidate
from a7p.factory import DistanceTable
from a7p import validator
from a7p.logger import logger, color_print, color_fmt

try:
    __version__ = metadata.version("a7p")
except metadata.PackageNotFoundError:
    __version__ = "undefined version"

# Define a global Semaphore with a maximum number of threads
MAX_THREADS = 5  # Set the maximum number of threads
semaphore = Semaphore(MAX_THREADS)

DISTANCES = {
    'subsonic': DistanceTable.SUBSONIC.value,
    'low': DistanceTable.LOW_RANGE.value,
    'medium': DistanceTable.MEDIUM_RANGE.value,
    'long': DistanceTable.LONG_RANGE.value,
    'ultra': DistanceTable.ULTRA_RANGE.value
}


async def limited_to_thread(func, *args):
    """Run a function in a thread, limited by the semaphore."""
    async with semaphore:  # Acquire the semaphore
        return await asyncio.to_thread(func, *args)


class CustomArgumentParser(ArgumentParser):
    def error(self, message):
        """Override error method to show help message on argument errors."""
        self.print_help(sys.stderr)
        # sys.stderr.write(f"\nError: {message}\n")
        logger.error(f"Error: {message}")
        sys.exit(2)

    def warning(self, message):
        """Override error method to show help message on argument errors."""
        self.print_help(sys.stderr)
        # sys.stderr.write(f"\nError: {message}\n")
        logger.warning(f"Error: {message}")
        sys.exit(2)


parser = CustomArgumentParser(
    f"a7p {__version__}",
    exit_on_error=True,
)
parser.add_argument("path", type=pathlib.Path, help="Path to the directory or file")
parser.add_argument('-V', '--version', action='version', version=__version__)
parser.add_argument('-r', '--recursive', action='store_true', help="Recursively walk files")
parser.add_argument('--unsafe', action='store_true', help="Skip validation")
parser.add_argument('--verbose', action='store_true', help="Verbose")
parser.add_argument('-F', '--force', action='store_true', help="Force changes saving")
# parser.add_argument('--json', action='store', type=pathlib.Path, help="Convert to/from JSON")

distances_group = parser.add_argument_group("Distances")
distances_group.add_argument('-zd', '--zero-distance', action='store', help="Set zero distance in meters",
                             type=int)
distances_group.add_argument('-d', '--distances', action='store', help="Set distances range",
                             choices=['subsonic', 'low', 'medium', 'long', 'ultra'])

zeroing_group = parser.add_argument_group("Zeroing")
zeroing_exclusive_group = zeroing_group.add_mutually_exclusive_group()
zeroing_exclusive_group.add_argument('-zs', '--zero-sync', action='store',
                                     type=pathlib.Path,
                                     help="Synchronize zero")
zeroing_exclusive_group.add_argument('-zo', '--zero-offset', action='store', nargs=2,
                                     type=float,
                                     help="Set clicks offset",
                                     metavar=("X_OFFSET", "Y_OFFSET"))


# zeroing_exclusive_group.add_argument('-cs', '--clicks-switch', action='store', nargs=4, help="Switch clicks sizes",
#                                      metavar=("CUR_X", "NEW_X", "CUR_Y", "NEW_Y"))


# parser.add_argument('--max-threads', action='store', type=int, default=5)



@dataclass
class Result:
    path: pathlib.Path
    error = None
    proto_violations: validator.Violations = None
    zero: tuple[float, float] = None
    new_zero: tuple[float, float] = None
    zero_update: bool = False
    distances: str = None
    zero_distance: str = None
    payload: object = None

    def print(self, verbose=False):
        valid = color_fmt("Invalid", levelname='ERROR') \
            if self.error \
            else color_fmt("Valid", levelname='INFO')

        print(f"{valid} File: {self.path.absolute()}")
        if self.zero:
            x, y = self.zero
            print("\tZero:\tX: {},\tY: {}".format(-x, y))
        if self.zero_update:
            x, y = self.new_zero
            color_print("\tNew zero:\tX: {},\tY: {}".format(-x, y), levelname='LIGHT_BLUE')
        if self.distances:
            color_print("\tNew range: {}".format(self.distances), levelname='LIGHT_BLUE')
        if self.zero_distance:
            color_print("\tNew zero distance: {}".format(self.zero_distance), levelname='LIGHT_BLUE')
        if self.error:
            color_print(f"{self.error}", levelname='ERROR')
            if verbose:
                self.print_violations()

    def print_violations(self):

        if self.proto_violations:
            for violation in self.proto_violations.ListFields():
                try:
                    violation_msg = []
                    for details in violation[1]:
                        violation_msg.extend([
                            color_fmt("\tViolation:", levelname="WARNING"),
                            f"\t\t{details.field_path}",
                            f"\t\t{details.constraint_id}",
                            f"\t\t{details.message}"
                        ])
                    print("\n".join(violation_msg))
                except Exception:
                    print(violation)

    def save_changes(self, force=False):
        if self.zero_distance or self.distances or self.zero_update:
            if not force:
                yes_no = input("Are you sure you want to save changes? Y/N: ")
                if yes_no.lower() != "y":
                    logger.info("Changes would not be saved")
                    return
            try:
                with open(self.path.absolute(), 'wb') as fp:
                    try:
                        A7PFile.dump(self.payload, fp, validate=True)
                        logger.info("Changes saved successfully")
                    except A7PDataError:
                        logger.warning("Invalid data, changes would not be saved")
            except IOError as e:
                logger.warning("Error while saving")


def update_distances(payload, distances, zero_distance):
    if not zero_distance:
        cur_zero_distance = payload.profile.distances[payload.profile.c_zero_distance_idx]
    else:
        cur_zero_distance = (zero_distance * 100)
    if distances:
        new_distances = [int(d * 100) for d in DISTANCES[distances]]
    else:
        new_distances = payload.profile.distances[:]
    new_distances.append(cur_zero_distance)
    new_distances = list(set(new_distances))
    new_distances.sort()
    payload.profile.distances[:] = new_distances
    payload.profile.c_zero_distance_idx = new_distances.index(cur_zero_distance)


def update_zeroing(payload, zero_offset=None, zero_sync=None):
    print(zero_sync, zero_offset)
    if zero_offset:
        x_offset, y_offset = zero_offset
        payload.profile.zero_x = payload.profile.zero_x + round(x_offset * -1000)
        payload.profile.zero_y = payload.profile.zero_y + round(y_offset * 1000)
    elif zero_sync:
        x_zero, y_zero = zero_sync
        payload.profile.zero_x = x_zero
        payload.profile.zero_y = y_zero


def update_data(payload, distances, zero_distance, zero_offset, zero_sync):
    update_distances(payload, distances, zero_distance)
    update_zeroing(payload, zero_offset, zero_sync)


def get_zero_to_sync(path, validate):
    try:
        with open(path, 'rb') as f:
            payload = A7PFile.load(f, validate)
        return payload.profile.zero_x, payload.profile.zero_y
    except (IOError, A7PDataError) as e:
        parser.error(e)


def process_file(
        path,
        validate=False,
        distances=None,
        zero_distance=None,
        zero_offset=None,
        zero_sync=None
):
    if path.suffix != ".a7p":
        return
    result = Result(
        path,
        distances=distances,
        zero_distance=zero_distance,
        zero_update=any([zero_offset, zero_sync])
    )
    try:
        with open(path, 'rb') as fp:
            data = fp.read()
        payload = A7PFile.loads(data, False)

        try:
            if validate:
                A7PFile.validate(payload)
        except A7PValidationError as e:
            result.error = "Validation error"
            result.proto_violations = e.violations
    except (IOError, A7PDataError) as e:
        result.error = e
        return result

    result.zero = (payload.profile.zero_x / 1000, payload.profile.zero_y / 1000)
    if distances or zero_distance or result.zero_update:
        update_data(payload, distances, zero_distance, zero_offset, zero_sync)

    result.new_zero = (payload.profile.zero_x / 1000, payload.profile.zero_y / 1000)

    result.payload = payload
    return result


async def process_files(
        path: pathlib.Path = None,
        recursive: bool = False,
        unsafe: bool = False,
        distances: str = None,
        zero_distance: int = None,
        json: pathlib.Path = None,
        verbose: bool = False,
        force: bool = False,
        zero_offset: tuple[float, float] = None,
        zero_sync: pathlib.Path = None
):
    if unsafe:
        logger.warning("Unsafe mode is restricted, it can corrupt your files")
    if force:
        logger.warning('Use the "force" option only if you are sure of what you are doing')
    validate = unsafe is False
    tasks = []

    if zero_sync:
        zero_sync = get_zero_to_sync(zero_sync, validate)

    if not path.is_dir():
        tasks.append(asyncio.to_thread(process_file, path, validate, distances, zero_distance, zero_offset, zero_sync))
    else:
        if json is not None:
            parser.warning("--json conversion available only for a single file")
        if recursive:
            item: pathlib.Path
            for item in path.rglob("*"):  # '*' matches all files and directories
                if item.is_file():
                    tasks.append(limited_to_thread(process_file, item, validate, distances, zero_distance, zero_offset,
                                                   zero_sync))
        else:
            for item in path.iterdir():
                if item.is_file():
                    tasks.append(limited_to_thread(process_file, item, validate, distances, zero_distance, zero_offset,
                                                   zero_sync))

    results: tuple[Result] = await asyncio.gather(*tasks)

    for result in results:
        if result:
            result.print(verbose)
            print()
            result.save_changes(force)


def main():
    # try:
        args = parser.parse_args()
        asyncio.run(process_files(**args.__dict__))
    # except Exception as e:
    #     logger.critical(e)


if __name__ == '__main__':
    main()
