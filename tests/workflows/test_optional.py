"""Test loading and serializing optional types."""

import pytest
from pathlib import Path

from polus.tools.workflows import CommandLineTool, Workflow, Process
from rich import print

from polus.tools.workflows.builders import StepBuilder, WorkflowBuilder
from polus.tools.workflows.utils import configure_folders

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)


@pytest.mark.parametrize("filename", ["uppercase2_wic_compatible2_optional.cwl"])
def test_load_clt(test_data_dir: Path, filename: str) -> None:
    """Test Command Line Tool factory method."""
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    serialized = clt.model_dump(exclude_none=True, by_alias=True, exclude={"name"})
    assert serialized["inputs"][0]["type"] == "string"
    assert serialized["inputs"][1]["type"] == "string?"


@pytest.mark.parametrize("filename", ["uppercase2_wic_compatible2_optional.cwl"])
def test_scattered_inputs(test_data_dir: Path, filename: str) -> None:
    """Test Command Line Tool factory method."""
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    scattered_inputs = [input_.id_ for input_ in clt.inputs]
    step = StepBuilder()(clt, scatter=scattered_inputs)
    print(step.model_dump(exclude_none=True, by_alias=True, exclude={"name"}))

    workflow = WorkflowBuilder()("optional_scatter_wf", steps=[step])
    print(workflow.model_dump(exclude_none=True, by_alias=True, exclude={"name"}))

    workflow.save(OUTPUT_DIR)
