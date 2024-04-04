"""Tests for any miscelleanous functions."""

from pathlib import Path

from polus.tools.workflows.default_ids import extract_name_from_id


def test_extract_name_from_id():
    """Test we can always correctly extract a name from id."""
    id_ = "file:///projects/polus-tools/tests/workflows/test_data/echo_string.cwl"
    assert extract_name_from_id(id_) == "echo_string"
    id_ = "echo_string"
    assert extract_name_from_id(id_) == "echo_string"
