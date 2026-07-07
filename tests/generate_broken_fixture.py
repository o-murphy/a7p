"""Regenerates tests/data/broken.a7p from tests/data/bc_ok.a7p.

Not part of the test suite (no `test_` prefix) - a maintenance script to
recreate the fixture if the invalid values it exercises ever need updating.
Run with: `uv run tests/generate_broken_fixture.py`
"""

from pathlib import Path

import a7p

DATA_DIR = Path(__file__).parent / "data"


def main() -> None:
    with open(DATA_DIR / "bc_ok.a7p", "rb") as fp:
        payload = a7p.load(fp, validate_=True)

    del payload.profile.distances[:]
    payload.profile.distances[:] = [10000000]
    del payload.profile.switches[3:]
    payload.profile.b_weight = 2000000
    payload.profile.c_muzzle_velocity = 100000
    payload.profile.short_name_top = "abcdefghij"

    with open(DATA_DIR / "broken.a7p", "wb") as fp:
        a7p.dump(payload, fp, False)


if __name__ == "__main__":
    main()
