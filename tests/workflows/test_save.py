"""Test saving processes."""
import pytest

from pathlib import Path
import logging

from polus.tools.workflows import CommandLineTool, Workflow
from polus.tools.workflows.utils import configure_folders


FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)


@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_save_clt(test_data_dir: Path, filename: str) -> None:
    """Test we can save a clt."""
    cwl_file = test_data_dir / filename
    new_model = CommandLineTool.load(cwl_file)
    new_model.save(path=OUTPUT_DIR)


@pytest.mark.parametrize("filename", ["workflow5.cwl"])
def test_save_workflow(test_data_dir: Path, filename: str) -> None:
    """Test we can save a workflow."""
    cwl_file = test_data_dir / filename
    wf1 = Workflow.load(cwl_file)
    wf1.save(path=OUTPUT_DIR)


@pytest.mark.parametrize("filename", ["subworkflow1.cwl"])
def test_save_subworkflow(test_data_dir: Path, filename: str) -> None:
    """Test we can save a workflow with a subworkflow."""
    cwl_file = test_data_dir / filename
    wf2 = Workflow.load(cwl_file)
    wf2.save(path=OUTPUT_DIR)


# TODO
@pytest.mark.skip(reason="not implemented")
def test_recursive_save() -> None:
    """Recursively saving all processes referenced."""
    # TODO CHECK We could add this capability if we want to bundle the whole workflow
    # description.
    pass
