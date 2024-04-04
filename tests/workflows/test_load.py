"""Test loading and parsing cwl files."""

import pytest
from pathlib import Path

from polus.tools.workflows import CommandLineTool, Workflow, Process
from polus.tools.workflows.exceptions import UnsupportedCwlVersionError


@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_load_clt(test_data_dir: Path, filename: str) -> None:
    """Test Command Line Tool factory method."""
    cwl_file = test_data_dir / filename
    CommandLineTool.load(cwl_file)


@pytest.mark.skip(reason="we decided to log a warning instead.")
@pytest.mark.parametrize("filename", ["echo_string_v10.cwl"])
def test_load_clt_old_version(test_data_dir: Path, filename: str) -> None:
    """Test Command Line Tool factory method."""
    with pytest.raises(UnsupportedCwlVersionError):
        cwl_file = test_data_dir / filename
        CommandLineTool.load(cwl_file)


@pytest.mark.parametrize(
    "filename", ["workflow5.cwl", "workflow7.cwl", "subworkflow1.cwl", "workflow3.cwl"]
)
def test_load_workflow(test_data_dir: Path, filename: str) -> None:
    """Test Workflow factory method."""
    cwl_file = test_data_dir / filename
    Workflow.load(cwl_file)


@pytest.mark.parametrize("filename", ["workflow3.cwl"])
def test_load_workflow_recursively(test_data_dir: Path, filename: str) -> None:
    """Test Workflow factory method."""
    cwl_file = test_data_dir / filename
    context = {}
    Workflow.load(cwl_file, recursive=True, context=context)
    assert len(context) == 3


@pytest.mark.parametrize("filename", ["workflow3_inline.cwl"])
def test_load_workflow_inlining(test_data_dir: Path, filename: str) -> None:
    """Test Workflow factory method when definitions can be arbitrarily inlined."""
    cwl_file = test_data_dir / filename

    # loading inlined definitions
    context = {}
    workflow = Workflow.load(cwl_file, context=context)
    assert len(context) == 1

    # loading recursively inlined definitions
    context = {}
    Workflow.load(cwl_file, context=context, recursive=True)
    assert len(context) == 3


@pytest.mark.parametrize("filename", ["echo_string.cwl", "workflow5.cwl"])
def test_load_process(test_data_dir: Path, filename: str) -> None:
    """Test Process factory method."""
    cwl_file = test_data_dir / filename
    Process.load(cwl_file)


@pytest.mark.parametrize("filename", ["workflow5.cwl"])
def test_recursive_load_workflow(test_data_dir: Path, filename: str) -> None:
    """Test Recursive load of processes."""
    cwl_file = test_data_dir / filename
    Process.load(cwl_file, recursive=True)


@pytest.mark.parametrize("filename", ["workflow3.cwl"])
def test_load_remote(test_data_dir: Path, filename: str) -> None:
    """Test load remote ref"""
    cwl_file = "https://raw.githubusercontent.com/PolusAI/image-workflows/1ae76425d681e67fdfcca792d6bd27080e971bde/cwl_adapters/file-renaming.cwl"
    clt = Process.load(cwl_file, recursive=True)
    assert len(clt._outputs) == 2
    assert (
        clt._outputs["preview_json"].format_ == "https://edamontology.org/format_3464"
    )
