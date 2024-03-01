"""Contains pytest config and general fixture definitions."""

import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture()
def test_data_dir() -> Path:
    """Return the path to the directory containing all test data."""
    return Path(__file__).parent.resolve() / "test_data"


@pytest.fixture()
def tmp_dir() -> Iterator[Path]:
    """Generate a temp staging dir for the test and returns its path.

    The staging dir will be deleted afterwards
    if the test run sucessfully.
    """
    tmp_dir = Path(tempfile.mkdtemp(suffix="tmp"))
    yield tmp_dir
    shutil.rmtree(tmp_dir)
