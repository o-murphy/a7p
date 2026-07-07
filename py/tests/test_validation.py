import pytest

import a7p
from a7p.exceptions import A7PValidationError


def test_valid_fixtures_pass(valid_a7p_path):
    with open(valid_a7p_path, "rb") as fp:
        a7p.load(fp, validate_=True, fail_fast=False)


def test_invalid_fixture_raises(invalid_a7p_path):
    with open(invalid_a7p_path, "rb") as fp:
        with pytest.raises(A7PValidationError) as exc_info:
            a7p.load(fp, validate_=True, fail_fast=False)

    assert exc_info.value.all_violations


def test_invalid_fixture_fail_fast_raises_on_first_violation(invalid_a7p_path):
    with open(invalid_a7p_path, "rb") as fp:
        with pytest.raises(A7PValidationError):
            a7p.load(fp, validate_=True, fail_fast=True)


def test_unsafe_load_skips_validation(broken_path):
    with open(broken_path, "rb") as fp:
        payload = a7p.load(fp, validate_=False)

    assert payload.profile is not None
