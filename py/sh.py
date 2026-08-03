# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "a7p",
# ]
# ///

import argparse
from pathlib import Path
import a7p
import fnmatch


def process_one(path, offset):
    try:
        with open(path, "rb") as fp:
            prof = a7p.load(fp, fail_fast=True)

        print(path, prof.profile.sc_height)

        if offset is not None:
            prof.profile.sc_height = prof.profile.sc_height + offset
            print(path, prof.profile.sc_height)
            with open(path, "wb") as fp:
                a7p.dump(prof, fp, fail_fast=True)
                print(f"OK: {path}")

    except Exception as e:
        print(f"ERROR: {e}: {path}")


def should_ignore(path: Path, ignore_patterns: list[str]) -> bool:
    """Checks if the path matches any of the ignore patterns."""
    if not ignore_patterns:
        return False

    path_str = str(path)
    path_name = path.name

    for pattern in ignore_patterns:
        # We check both the full path and the file name
        if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path_name, pattern):
            return True
        # Check if any part of the path matches the pattern
        if any(fnmatch.fnmatch(part, pattern) for part in path.parts):
            return True

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Handling .a7p files with the ability to change sc_height"
    )
    parser.add_argument("dir", type=Path, help="Processing directory")
    parser.add_argument("-o", "--offset", type=int, help="Offset for sc_height")
    parser.add_argument(
        "-i",
        "--ignore",
        action="append",
        help="Pattern to ignore (can be specified multiple times). Examples: '*.backup', 'temp/*', 'test_*'",
    )

    ns = parser.parse_args()
    ignore_patterns = ns.ignore or []

    for fp in tuple(p for p in ns.dir.rglob("*") if p.is_file() and p.suffix == ".a7p"):
        if should_ignore(fp, ignore_patterns):
            print(f"IGNORED: {fp}")
            continue
        process_one(fp, ns.offset)


if __name__ == "__main__":
    main()
