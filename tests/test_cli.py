from a7p import profedit_pb2
from a7p.__main__ import (
    Result,
    process_file,
    update_distances,
    update_switches,
    update_zeroing,
)


def test_process_file_valid(bc_ok_path):
    result = process_file(bc_ok_path, validate=True)
    assert result.error is None
    assert result.payload is not None
    assert result.zero == (
        result.payload.profile.zero_x / 1000,
        result.payload.profile.zero_y / 1000,
    )


def test_process_file_invalid(broken_path):
    result = process_file(broken_path, validate=True, verbose=True)
    assert result.error == "Validation error"
    assert result.validation_error is not None
    assert result.validation_error.all_violations


def test_process_file_ignores_non_a7p_suffix(tmp_path):
    other = tmp_path / "note.txt"
    other.write_text("not an a7p file")
    assert process_file(other, validate=True) is None


def test_process_file_unsafe_skips_validation(broken_path):
    result = process_file(broken_path, validate=False)
    assert result.error is None
    assert result.payload is not None


def test_update_zeroing_offset(bc_ok_payload):
    payload = bc_ok_payload
    zero_x, zero_y = payload.profile.zero_x, payload.profile.zero_y
    update_zeroing(payload, zero_offset=(1.0, 2.0))
    assert payload.profile.zero_x == zero_x - 1000
    assert payload.profile.zero_y == zero_y + 2000


def test_update_zeroing_sync(bc_ok_payload):
    payload = bc_ok_payload
    update_zeroing(payload, zero_sync=(123, 456))
    assert payload.profile.zero_x == 123
    assert payload.profile.zero_y == 456


def test_update_distances_appends_zero_distance(bc_ok_payload):
    payload = bc_ok_payload
    update_distances(payload, distances="subsonic", zero_distance=77)
    assert 7700 in payload.profile.distances
    assert payload.profile.distances[payload.profile.c_zero_distance_idx] == 7700


def test_update_switches_replaces_all(bc_ok_payload):
    payload = bc_ok_payload
    new_switches = [profedit_pb2.SwPos(c_idx=1, zoom=1)]
    update_switches(payload, new_switches)
    assert list(payload.profile.switches) == new_switches


def test_save_changes_writes_file(tmp_path, bc_ok_payload):
    out_path = tmp_path / "out.a7p"
    result = Result(out_path, zero_update=True, payload=bc_ok_payload)
    result.save_changes(force=True)
    assert out_path.exists()
