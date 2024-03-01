"""Test loading and parsing cwl files."""

import pytest
from pathlib import Path

from polus.tools.workflows import CommandLineTool, Workflow, Process


@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_load_clt(test_data_dir: Path, filename: str) -> None:
    """Test Command Line Tool factory method."""
    cwl_file = test_data_dir / filename
    CommandLineTool.load(cwl_file)


@pytest.mark.xfail(reason="only cwl v1.2 is supported.")
@pytest.mark.parametrize("filename", ["echo_string_v10.cwl"])
def test_load_clt_old_version(test_data_dir: Path, filename: str) -> None:
    """Test Command Line Tool factory method."""
    cwl_file = test_data_dir / filename
    CommandLineTool.load(cwl_file)


@pytest.mark.parametrize(
    "filename", ["workflow5.cwl", "workflow7.cwl", "subworkflow1.cwl", "workflow3.cwl"]
)
def test_load_workflow(test_data_dir: Path, filename: str) -> None:
    """Test Workflow factory method."""
    cwl_file = test_data_dir / filename
    Workflow.load(cwl_file)


@pytest.mark.parametrize("filename", ["echo_string.cwl", "workflow5.cwl"])
def test_load_process(test_data_dir: Path, filename: str) -> None:
    """Test Process factory method."""
    cwl_file = test_data_dir / filename
    Process.load(cwl_file)


# TODO So cwlparser does not check the referenced clts,
# It justs check the definition is valid at the first level.
# So if we wanted to more validation, we would need to recursively pull all references.
# NOTE we could provide a Context object to collect definition
# instead of parsing clts over and over.
@pytest.mark.parametrize("filename", ["workflow5.cwl"])
def test_recursive_load_workflow(test_data_dir: Path, filename: str) -> None:
    """Test Recursive load of processes."""
    cwl_file = test_data_dir / filename
    Process.load(cwl_file, recursive=True)
