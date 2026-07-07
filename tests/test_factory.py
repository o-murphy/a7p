import pytest

import a7p
from a7p.factory import A7PFactory, DistanceTable


def test_default_factory_produces_valid_payload():
    payload = A7PFactory()
    a7p.validate(payload, fail_fast=False)  # raises on failure


def test_default_factory_field_values():
    payload = A7PFactory()
    assert payload.profile.profile_name == "New profile"
    assert len(payload.profile.switches) == 4
    assert len(payload.profile.coef_rows) == 1


@pytest.mark.parametrize(
    "table",
    [
        DistanceTable.SUBSONIC,
        DistanceTable.LOW_RANGE,
        DistanceTable.MEDIUM_RANGE,
        DistanceTable.LONG_RANGE,
        DistanceTable.ULTRA_RANGE,
    ],
)
def test_factory_accepts_all_distance_tables(table):
    payload = A7PFactory(distances=table)
    assert len(payload.profile.distances) == len(table.value)
    a7p.validate(payload, fail_fast=False)


def test_factory_accepts_custom_distance_tuple():
    payload = A7PFactory(distances=(100.0, 200.0, 300.0))
    assert list(payload.profile.distances) == [10000, 20000, 30000]


def test_factory_rejects_empty_distances():
    with pytest.raises(ValueError):
        A7PFactory(distances=())


def test_factory_rejects_invalid_distances_type():
    with pytest.raises(ValueError):
        A7PFactory(distances="not-a-table")
