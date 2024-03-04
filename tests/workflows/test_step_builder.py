"""Test we can build a step from a cwl clt file."""

from pathlib import Path

import pytest
from polus.tools.workflows import CommandLineTool
from polus.tools.workflows import StepBuilder


@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_step_builder(test_data_dir: Path, filename: str) -> None:
    """Test we can build a step from a cwl clt file."""
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    StepBuilder()(clt)
