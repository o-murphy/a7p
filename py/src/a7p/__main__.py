import asyncio
import sys
from argparse import ArgumentParser
from asyncio import Semaphore
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path

from tqdm.asyncio import tqdm_asyncio

import a7p
from a7p import exceptions, profedit_pb2
from a7p.exceptions import A7PValidationError
from a7p.factory import DistanceTable
from a7p.logger import logger, color_print, color_fmt
from a7p.recover.recover_process import attempt_to_recover

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

parser.add_argument("path", type=Path,
                    help="Specify the path to the directory or a .a7p file to process.")

# Main options
parser.add_argument('-V', '--version', action='version', version=__version__,
                    help="Display the current version of the tool.")
parser.add_argument('-r', '--recursive', action='store_true',
                    help="Recursively process files in the specified directory.")
parser.add_argument('-F', '--force', action='store_true',
                    help="Force saving changes without confirmation.")
parser.add_argument('--unsafe', action='store_true',
                    help="Skip data validation (use with caution).")

recover_group = parser.add_argument_group("Single file specific options")
recover_group.add_argument('--verbose', action='store_true',
                           help="Enable verbose output for detailed logs. "
                                "This option is only allowed for a single file.")
recover_group.add_argument('--recover', action='store_true',
                           help="Attempt to recover from errors found in a file. "
                                "This option is only allowed for a single file.")

# Distances group
distances_group = parser.add_argument_group("Distances")
distances_group.add_argument('-zd', '--zero-distance', action='store', type=int,
                             help="Set the zero distance in meters.")
distances_group.add_argument('-d', '--distances', action='store',
                             choices=['subsonic', 'low', 'medium', 'long', 'ultra'],
                             help="Specify the distance range: 'subsonic', 'low', 'medium', 'long', or 'ultra'.")

# Zeroing group
zeroing_group = parser.add_argument_group("Zeroing")
zeroing_exclusive_group = zeroing_group.add_mutually_exclusive_group()
zeroing_exclusive_group.add_argument('-zs', '--zero-sync', action='store', type=Path,
                                     help="Synchronize zero using a specified configuration file.")
zeroing_exclusive_group.add_argument('-zo', '--zero-offset', action='store', nargs=2, type=float,
                                     metavar=("X_OFFSET", "Y_OFFSET"),
                                     help="Set the offset for zeroing in clicks (X_OFFSET and Y_OFFSET).")


# zeroing_exclusive_group.add_argument('-cs', '--clicks-switch', action='store', nargs=4, help="Switch clicks sizes",
#                                      metavar=("CUR_X", "NEW_X", "CUR_Y", "NEW_Y"))

# Switches group (Archer devices specific)
switches_group = parser.add_argument_group("Switches")
switches_exclusive_group = switches_group.add_mutually_exclusive_group()
switches_exclusive_group.add_argument('-cps', '--copy-switches-from', action='store', type=Path,
                                      help="Copy switches from other a7p file.", dest="copy_switches")

# parser.add_argument('--max-threads', action='store', type=int, default=5)


@dataclass
class Result:
    path: Path
    error = None
    validation_error: A7PValidationError | None = None
    zero: tuple[float, float] = None
    new_zero: tuple[float, float] = None
    zero_update: bool = False
    distances: str = None
    zero_distance: str = None
    recover: bool = False
    payload: profedit_pb2.Payload = None
    switches: bool = False

    def reset_errors(self):
        self.error = None
        self.validation_error = None

    def print(self, verbose=False):

        if self.error:
            error = color_fmt(f"Invalid ({self.error}):", levelname='ERROR')
            print(f'{error} File: {self.path.absolute()}')

        else:
            print(f'{color_fmt("Valid:", levelname="INFO")} File: {self.path.absolute()}')

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
        if self.switches:
            color_print("\tSwitches copied", levelname='LIGHT_BLUE')

        if self.validation_error and verbose:
            for violation in self.validation_error.all_violations:
                color_print(violation.format(), levelname='WARNING')

    def save_changes(self, force=False):
        if self.zero_distance or self.distances or self.zero_update or self.recover:
            if not force:
                yes_no = input(color_fmt("Do you want to save changes? (Y/N): ", levelname="LIGHT_YELLOW"))
                if yes_no.lower() != "y":
                    logger.info("No changes have been saved.")
                    return
            try:
                try:
                    # Serialize and validate the payload
                    data = a7p.dumps(self.payload)

                    # Write the validated data to the file
                    filepath = self.path.absolute()
                    if self.recover:
                        filepath = filepath.with_name(filepath.stem + "_recovered" + filepath.suffix)

                    with open(filepath, 'wb') as fp:
                        fp.write(data)
                        logger.info(f"Changes have been saved successfully to {filepath}.")
                except exceptions.A7PDataError:
                    logger.warning("The data is invalid. Changes have not been saved.")
            except IOError as e:
                logger.warning(f"An error occurred while saving: {e}")


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
    if zero_offset:
        x_offset, y_offset = zero_offset
        payload.profile.zero_x = payload.profile.zero_x + round(x_offset * -1000)
        payload.profile.zero_y = payload.profile.zero_y + round(y_offset * 1000)
    elif zero_sync:
        x_zero, y_zero = zero_sync
        payload.profile.zero_x = x_zero
        payload.profile.zero_y = y_zero


def update_switches(payload, switches):
    if switches:
        del payload.profile.switches[:]
        payload.profile.switches.extend(switches)


def update_data(payload, distances, zero_distance, zero_offset, zero_sync, copy_switches):
    update_distances(payload, distances, zero_distance)
    update_zeroing(payload, zero_offset, zero_sync)
    update_switches(payload, copy_switches)


def get_zero_to_sync(path, validate):
    try:
        with open(path, 'rb') as f:
            payload = a7p.load(f, validate_=validate, fail_fast=True)
        return payload.profile.zero_x, payload.profile.zero_y
    except (IOError, exceptions.A7PDataError) as e:
        parser.error(e)


def get_switches_to_copy(path, validate):
    try:
        with open(path, 'rb') as f:
            payload = a7p.load(f, validate_=validate, fail_fast=True)
        return payload.profile.switches
    except (IOError, exceptions.A7PDataError) as e:
        parser.error(e)


def process_file(
        path,
        validate=False,
        distances=None,
        zero_distance=None,
        zero_offset=None,
        zero_sync=None,
        verbose=False,
        recover=False,
        copy_switches=None,
):
    if path.suffix != ".a7p":
        return
    result = Result(
        path,
        distances=distances,
        zero_distance=zero_distance,
        zero_update=any([zero_offset, zero_sync]),
        switches = copy_switches is not None
    )
    try:
        with open(path, 'rb') as fp:
            data = fp.read()
        try:
            payload = a7p.loads(data, validate_=validate, fail_fast=verbose == False)
        except exceptions.A7PValidationError as err:
            result.error = "Validation error"
            result.validation_error = err
            payload = err.payload
    except (IOError, exceptions.A7PDataError) as err:
        result.error = err
        return result

    result.zero = (payload.profile.zero_x / 1000, payload.profile.zero_y / 1000)
    if distances or zero_distance or result.zero_update or copy_switches:
        update_data(payload, distances, zero_distance, zero_offset, zero_sync, copy_switches)

    result.new_zero = (payload.profile.zero_x / 1000, payload.profile.zero_y / 1000)

    result.payload = payload

    if recover:
        recover_payload(result)

    return result


async def print_results_and_save(results, verbose=False, force=False):
    count_errors = 0
    results = sorted(filter(lambda x: x is not None, results),
                     key=lambda x: x.error is not None, reverse=False)
    for result in results:
        if result:
            result.print(verbose)
            print()
            result.save_changes(force)

            if result.error:
                count_errors += 1

    output_strings = [
        f"Files checked: {len(results)}",
        color_fmt(f"Ok: {len(results) - count_errors}", levelname="INFO"),
        color_fmt(f"Failed: {count_errors}", levelname="ERROR"),
    ]
    print(", ".join(output_strings))


def recover_payload(result: Result):
    if result.validation_error:
        result.recover = True

        color_print("Violations found:", levelname="ERROR")
        for v in result.validation_error.all_violations:
            color_print(v.format(), levelname="WARNING")

        recover_error = attempt_to_recover(result.validation_error)
        if not recover_error:
            result.reset_errors()

    else:
        logger.info("No violations found")


async def process_files(
        path: Path = None,
        recursive: bool = False,
        unsafe: bool = False,
        distances: str = None,
        zero_distance: int = None,
        json: Path = None,
        verbose: bool = False,
        force: bool = False,
        zero_offset: tuple[float, float] = None,
        zero_sync: Path = None,
        recover: bool = False,
        copy_switches: Path = None,
):
    if not Path.exists(path):
        parser.warning(f"The '{path}' is not a valid path")
    if unsafe:
        logger.warning("The 'unsafe' mode is restricted and may lead to file corruption.")
    if force:
        logger.warning("Use the 'force' option cautiously, only if you are certain about its effects.")

    validate = unsafe is False
    tasks = []

    if zero_sync:
        zero_sync = get_zero_to_sync(zero_sync, validate)

    if copy_switches:
        copy_switches = get_switches_to_copy(copy_switches, validate)

    if not path.is_dir():
        if path and recover:

            invalid_options_for_recover = [
                recursive, unsafe, distances, zero_distance, json,
                verbose, force, zero_offset, zero_sync, copy_switches,
            ]

            if any(invalid_options_for_recover):
                raise parser.error(f"The '--recover' option cannot be combined with other options.")

            verbose = True

        results = [await asyncio.to_thread(process_file,
                                           path, validate, distances,
                                           zero_distance, zero_offset, zero_sync,
                                           verbose, recover, copy_switches
                                           )]
    else:
        if recover:
            parser.warning("The '--recover' option is supported only when processing a single file.")
        if verbose:
            parser.warning("The '--verbose' option is supported only when processing a single file.")

        if recursive:
            item: Path
            for item in path.rglob("*"):  # '*' matches all files and directories
                if item.is_file():
                    tasks.append(limited_to_thread(
                        process_file, item, validate, distances,
                        zero_distance, zero_offset, zero_sync, copy_switches))
        else:
            for item in path.iterdir():
                if item.is_file():
                    tasks.append(limited_to_thread(process_file, item, validate, distances,
                                                   zero_distance, zero_offset, zero_sync, copy_switches))

        results: tuple[Result] | list[Result] = await tqdm_asyncio.gather(*tasks)

    await print_results_and_save(results, verbose=verbose, force=force)


def main():
    try:
        args = parser.parse_args()
        asyncio.run(process_files(**args.__dict__))
    except NotImplementedError as e:
        logger.error(e)
        sys.exit(0)
    except Exception as e:
        logger.critical(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        logger.warning("Process interrupted by user. Exiting gracefully...")
        sys.exit(0)
    logger.info("Process completed successfully. Exiting gracefully...")
    sys.exit(0)


if __name__ == '__main__':
    main()
