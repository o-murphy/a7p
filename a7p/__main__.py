import asyncio
import pathlib
import sys
from argparse import ArgumentParser
from asyncio import Semaphore
from dataclasses import dataclass
from importlib import metadata

from a7p import A7PFile, A7PDataError
from a7p import protovalidate
from a7p.factory import DistanceTable
from a7p.protovalidate import ValidationError, Violations

try:
    __version__ = metadata.version("a7p")
except metadata.PackageNotFoundError:
    __version__ = "undefined version"

# Define a global Semaphore with a maximum number of threads
MAX_THREADS = 5  # Set the maximum number of threads
semaphore = Semaphore(MAX_THREADS)


async def limited_to_thread(func, *args):
    """Run a function in a thread, limited by the semaphore."""
    async with semaphore:  # Acquire the semaphore
        return await asyncio.to_thread(func, *args)


class CustomArgumentParser(ArgumentParser):
    def error(self, message):
        """Override error method to show help message on argument errors."""
        self.print_help(sys.stderr)
        sys.stderr.write(f"\nError: {message}\n")
        sys.exit(2)


parser = CustomArgumentParser(
    f"a7p {__version__}",
    exit_on_error=True,
)
parser.add_argument("path", type=pathlib.Path, help="Path to the directory or file")
parser.add_argument('-V', '--version', action='version', version=__version__)
parser.add_argument('-r', '--recursive', action='store_true', help="Recursively walk files")
parser.add_argument('-v', '--validate', action='store_true', help="Validate files")
parser.add_argument('--verbose', action='store_true', help="Verbose")
parser.add_argument('-F', '--force', action='store_true', help="Force changes saving")
# parser.add_argument('--json', action='store', type=pathlib.Path, help="Convert to/from JSON")

distances_group = parser.add_argument_group("Distances")
distances_group.add_argument('-zd', '--zero-distance', action='store', help="Set zero distance in meters",
                    type=int)
distances_group.add_argument('-d', '--distances', action='store', help="Set distances range",
                    choices=['subsonic', 'low', 'medium', 'long', 'ultra'])

# group = parser.add_argument_group("Zeroing")


# group.add_argument('-zs', '--zero-sync', action='store_true', help="Synchronize zero")
# group.add_argument('-zo', '--zero-offset', action='store', nargs=2, help="Set clicks offset",
#                     metavar=("X_OFFSET", "Y_OFFSET"))
# group.add_argument('-cs', '--clicks-switch', action='store', nargs=4, help="Switch clicks sizes",
#                     metavar=("CUR_X", "NEW_X", "CUR_Y", "NEW_Y"))

# parser.add_argument('--max-threads', action='store', type=int, default=5)


@dataclass
class Result:
    path: pathlib.Path
    error = None
    violations: Violations = None
    zero: tuple[float, float] = None
    distances: str = None
    zero_distance: str = None
    payload: object = None

    def print(self):
        print(f"File: {self.path.absolute()}")
        if self.zero:
            print("Zero: X: {}, Y: {}".format(*self.zero))
        if self.error:
            print(f"Error: {self.error}")

        if self.distances:
            print("New range: {}".format(self.distances))

        if self.zero_distance:
            print("New zero distance: {}".format(self.zero_distance))

    def details(self):

        if self.violations:
            for violation in self.violations.ListFields():
                try:
                    violation_msg = []
                    for details in violation[1]:
                        violation_msg.extend([
                            "\tViolation:"
                            f"\t\t{details.field_path}",
                            f"\t\t{details.constraint_id}",
                            f"\t\t{details.message}"
                        ])
                    print("\n".join(violation_msg))
                except Exception:
                    print(violation)

    def save_changes(self):
        if self.zero_distance or self.distances:
            try:
                with open(self.path.absolute(), 'wb') as fp:
                    try:
                        A7PFile.dump(self.payload, fp, validate=True)
                    except ValidationError:
                        print("Invalid data, changes would not be saved")
            except IOError as e:
                print("Error while saving")


DISTANCES = {
    'subsonic': DistanceTable.SUBSONIC.value,
    'low': DistanceTable.LOW_RANGE.value,
    'medium': DistanceTable.MEDIUM_RANGE.value,
    'long': DistanceTable.LONG_RANGE.value,
    'ultra': DistanceTable.ULTRA_RANGE.value
}


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


def update_data(payload, distances, zero_distance):
    update_distances(payload, distances, zero_distance)


def process_file(
        path,
        validate=False,
        distances=None,
        zero_distance=None
):
    if path.suffix != ".a7p":
        return
    result = Result(
        path,
        distances=distances,
        zero_distance=zero_distance
    )
    try:
        with open(path, 'rb') as fp:
            data = fp.read()
        payload = A7PFile.loads(data, False)

        try:
            if validate:
                protovalidate.validate(payload)
        except ValidationError as e:
            result.error = "Validation error"
            result.violations = e.violations
    except (IOError, A7PDataError) as e:
        result.error = e
        return result

    if distances or zero_distance:
        update_data(payload, distances, zero_distance)

    result.zero = (payload.profile.zero_x / 1000, payload.profile.zero_y / 1000)
    result.payload = payload
    return result


async def process_files(
        path: pathlib.Path = None,
        recursive: bool = False,
        validate: bool = False,
        distances: str = None,
        zero_distance: int = None,
        json: pathlib.Path = None,
        verbose: bool = False,
        force: bool = False,
):
    tasks = []

    if not path.is_dir():
        tasks.append(asyncio.to_thread(process_file, path, validate, distances, zero_distance))
    else:
        if json is not None:
            parser.error("--json conversion available only for a single file")
        if recursive:
            item: pathlib.Path
            for item in path.rglob("*"):  # '*' matches all files and directories
                if item.is_file():
                    tasks.append(limited_to_thread(process_file, item, validate, distances, zero_distance))
        else:
            for item in path.iterdir():
                if item.is_file():
                    tasks.append(limited_to_thread(process_file, item, validate, distances, zero_distance))

    results: tuple[Result] = await asyncio.gather(*tasks)

    for result in results:
        if result:
            result.print()
            if verbose:
                result.details()
            if force:
                result.save_changes()
            else:
                yes_no = input("Are you sure you want to save changes? Y/N: ")
                if yes_no.lower() == "y":
                    result.save_changes()
                else:
                    print("Changes would not be saved")


def main():
    args = parser.parse_args()
    asyncio.run(process_files(**args.__dict__))


if __name__ == '__main__':
    main()
