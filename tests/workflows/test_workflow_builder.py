"""Test the workflow builder."""

from pathlib import Path

import pytest
from polus.tools.workflows import CommandLineTool
from polus.tools.workflows import StepBuilder
from polus.tools.workflows import Workflow
from polus.tools.workflows import WorkflowBuilder
from polus.tools.workflows import run_cwl
from polus.tools.workflows.model import WorkflowStep
from polus.tools.workflows.utils import configure_folders

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)


@pytest.mark.parametrize(
    "clts",
    [["echo_string.cwl", "uppercase2_wic_compatible2.cwl"]],
)
def test_workflow_builder(test_data_dir: Path, clts: list[str]) -> None:
    """Build a basic workflow from steps."""
    steps_input_count = 0
    steps_output_count = 0
    steps = []
    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        step = StepBuilder()(clt)
        steps_input_count += len(step.in_)
        steps_output_count += len(step.out)
        steps.append(step)
    wf_builder = WorkflowBuilder(workdir=OUTPUT_DIR)
    wf: Workflow = wf_builder("wf3", steps=steps)

    input_count = len(wf.inputs)
    assert (
        input_count == steps_input_count
    ), f"workflow should have {steps_input_count} input, got {input_count}."
    output_count = len(wf.outputs)
    assert (
        output_count == steps_output_count
    ), f"workflow should have {steps_output_count} input, got {output_count}."


@pytest.mark.parametrize(
    "clts",
    [["echo_string.cwl", "uppercase2_wic_compatible2.cwl"]],
)
def test_workflow_builder_with_linked_steps(
    test_data_dir: Path,
    clts: list[str],
) -> None:
    """Build a basic workflow from steps and link their ios."""
    steps_input_count = 0
    steps_output_count = 0
    steps: list[WorkflowStep] = []
    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        step = StepBuilder()(clt)
        steps_input_count += len(step.in_)
        steps_output_count += len(step.out)
        steps.append(step)

    # link steps
    (step1, step2) = steps
    step2.message = step1.message_string
    step2.uppercase_message = step1.message_string

    wf_builder = WorkflowBuilder(workdir=OUTPUT_DIR)
    wf: Workflow = wf_builder("wf3", steps=steps)

    input_count = len(wf.inputs)
    # we have linked 2 inputs from the second step
    # so they should not be part of the final model.
    expected_count = steps_input_count - 2
    assert (
        input_count == expected_count
    ), f"workflow should have {expected_count} input, got {input_count}."


@pytest.mark.parametrize(
    "clts",
    [["echo_string.cwl", "uppercase2_wic_compatible2.cwl", "touch_single.cwl"]],
)
def test_workflow_builder_with_subworkflows(
    test_data_dir: Path,
    clts: list[str],
) -> None:
    """Build and run a workflow containing another workflow and link their ios."""
    steps = []
    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        step = StepBuilder()(clt)
        steps.append(step)

    (step1, step2, step3) = steps
    step2.message = step1.message_string
    step2.uppercase_message = step1.message_string

    wf_builder = WorkflowBuilder(workdir=OUTPUT_DIR)
    wf: Workflow = wf_builder("wf3", steps=[step1, step2])
    step12 = StepBuilder()(wf)

    step3.touchfiles = step12.out[0]
    # equivalent to :
    # step3.touchfiles = (
    #     step12.wf3___1__step__uppercase2_wic_compatible2___uppercase_message

    wf_builder = WorkflowBuilder(workdir=OUTPUT_DIR)
    main_wf = wf_builder("wf4", steps=[step12, step3])

    step4 = StepBuilder()(main_wf)

    step4.in_[0].value = "test_message"
    # equivalent to :

    config = step4.save_config(OUTPUT_DIR)

    run_cwl(OUTPUT_DIR / f"{main_wf.name}.cwl", config_file=config, cwd=STAGING_DIR)
