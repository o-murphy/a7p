"""Regression tests for schema_validator.py bounds, exercised through the
public a7p.validate() -- these confirm the schema-based validator that
actually backs a7p.validate() preserves the intended decisions, in
particular the two that were open design questions until confirmed against
profile.clj / real data:

- c_idx: 0-200 or the 255 "unused" sentinel; 201-254 is an undefined gap and
  must be rejected (a7p-js/a7p-dart are currently looser here -- see
  schema/a7p.schema.json's c_idx.x-discrepancy).
- switches[].distance: 0 ("unused") or [100, 300000], regardless of
  distance_from -- not treated as an index into `distances` when
  distance_from == INDEX (a7p-js/a7p-dart do treat it that way -- see
  schema/a7p.schema.json's distance.x-discrepancy). profile.clj itself is
  not touched; this only pins down a7p-py's behavior.
"""

import pytest

import a7p
from a7p.exceptions import A7PValidationError


def is_valid(payload) -> bool:
    try:
        a7p.validate(payload, fail_fast=True)
        return True
    except A7PValidationError:
        return False


@pytest.mark.parametrize(
    "zoom, expected", [(0, True), (4, True), (6, True), (7, False)]
)
def test_switch_zoom_bounds(build_payload, default_switch, zoom, expected):
    payload = build_payload({"switches": [default_switch(zoom=zoom) for _ in range(4)]})
    assert is_valid(payload) is expected


@pytest.mark.parametrize(
    "c_idx, expected",
    [(0, True), (200, True), (201, False), (254, False), (255, True)],
)
def test_switch_c_idx_bounds(build_payload, default_switch, c_idx, expected):
    payload = build_payload(
        {"switches": [default_switch(c_idx=c_idx) for _ in range(4)]}
    )
    assert is_valid(payload) is expected


@pytest.mark.parametrize(
    "distance, expected",
    [(0, True), (50, False), (100, True), (300000, True), (300001, False)],
)
@pytest.mark.parametrize("distance_from", ["VALUE", "INDEX"])
def test_switch_distance_bounds_independent_of_distance_from(
    build_payload, default_switch, distance_from, distance, expected
):
    """distance is either 0 (unused) or in [100, 300000], regardless of
    distance_from - it is not treated as an index when distance_from is
    INDEX (that would be a divergence from profile.clj)."""
    payload = build_payload(
        {
            "switches": [
                default_switch(distance_from=distance_from, distance=distance)
                for _ in range(4)
            ]
        }
    )
    assert is_valid(payload) is expected


@pytest.mark.parametrize("count, expected", [(3, False), (4, True), (5, True)])
def test_switches_min_count(build_payload, default_switch, count, expected):
    payload = build_payload({"switches": [default_switch() for _ in range(count)]})
    assert is_valid(payload) is expected


@pytest.mark.parametrize("b_length, expected", [(9, False), (10, True)])
def test_b_length_lower_bound(build_payload, b_length, expected):
    payload = build_payload({"b_length": b_length})
    assert is_valid(payload) is expected


@pytest.mark.parametrize("bc_type", ["G1", "G7"])
@pytest.mark.parametrize("bc_cd, expected", [(100000, True), (100001, False)])
def test_coef_row_bc_cd_bound_g1_g7(build_payload, bc_type, bc_cd, expected):
    payload = build_payload(
        {"bc_type": bc_type, "coef_rows": [{"bc_cd": bc_cd, "mv": 0}]}
    )
    assert is_valid(payload) is expected


@pytest.mark.parametrize("bc_cd, expected", [(100000, True), (100001, False)])
def test_coef_row_bc_cd_bound_custom(build_payload, bc_cd, expected):
    payload = build_payload(
        {"bc_type": "CUSTOM", "coef_rows": [{"bc_cd": bc_cd, "mv": 0}]}
    )
    assert is_valid(payload) is expected


@pytest.mark.parametrize("mv, expected", [(100000, True), (100001, False)])
def test_coef_row_mv_bound_custom(build_payload, mv, expected):
    payload = build_payload(
        {"bc_type": "CUSTOM", "coef_rows": [{"bc_cd": 0, "mv": mv}]}
    )
    assert is_valid(payload) is expected


def test_coef_row_mv_must_be_unique_except_zero(build_payload):
    payload = build_payload(
        {
            "bc_type": "G1",
            "coef_rows": [{"bc_cd": 0, "mv": 100}, {"bc_cd": 0, "mv": 100}],
        }
    )
    assert is_valid(payload) is False


def test_coef_row_mv_zero_duplicates_allowed(build_payload):
    payload = build_payload(
        {
            "bc_type": "G1",
            "coef_rows": [{"bc_cd": 0, "mv": 0}, {"bc_cd": 0, "mv": 0}],
        }
    )
    assert is_valid(payload) is True


def test_minimal_payload_is_valid(build_payload):
    assert is_valid(build_payload()) is True


@pytest.mark.parametrize(
    "field",
    [
        "profile_name",
        "cartridge_name",
        "bullet_name",
        "short_name_top",
        "short_name_bot",
        "caliber",
    ],
)
def test_required_string_fields_may_be_empty(build_payload, field):
    """None of the required string fields have a minLength -- devices ship
    real profiles with these left unset (empty string)."""
    payload = build_payload({field: ""})
    assert is_valid(payload) is True
