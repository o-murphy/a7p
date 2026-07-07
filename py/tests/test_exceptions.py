from pathlib import Path

from a7p.exceptions import (
    A7PValidationError,
    A7PYupyValidationError,
    Violation,
    YupyViolation,
)


def test_violation_format_with_scalar_value():
    v = Violation(path="~/profile/zero_x", value=42, reason="out of range")
    formatted = v.format()
    assert "~/profile/zero_x" in formatted
    assert "42" in formatted
    assert "out of range" in formatted


def test_violation_format_with_path_object():
    v = Violation(path=Path("~/profile"), value=1, reason="bad")
    assert "profile" in v.format()


def test_violation_format_hides_non_scalar_value():
    v = Violation(path="~", value={"nested": "object"}, reason="bad")
    assert "<object>" in v.format()


def test_all_violations_combines_general_and_yupy():
    yupy_violations = [YupyViolation(path="~/a", value=1, reason="r1")]
    err = A7PValidationError(
        "Validation error",
        payload=None,
        violations=[Violation(path="~", value=None, reason="top-level")],
        yupy_violations=yupy_violations,
    )
    assert err.all_violations == [
        Violation(path="~", value=None, reason="top-level"),
        yupy_violations[0],
    ]


def test_all_violations_defaults_to_empty_lists():
    err = A7PValidationError("Validation error", payload=None)
    assert err.all_violations == []


def test_a7p_yupy_validation_error_sets_yupy_violations():
    violations = [YupyViolation(path="~/x", value=1, reason="bad")]
    err = A7PYupyValidationError("Yupy error", payload=None, violations=violations)
    assert err.yupy_violations == violations
    assert err.all_violations == violations
