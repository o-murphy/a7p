from pathlib import Path

from a7p.exceptions import A7PValidationError, Violation


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


def test_violations_defaults_to_empty_list():
    err = A7PValidationError("Validation error", payload=None)
    assert err.violations == []


def test_violations_carries_given_list():
    violations = [Violation(path="~/x", value=1, reason="bad")]
    err = A7PValidationError("Validation error", payload=None, violations=violations)
    assert err.violations == violations
