"""Test conditional clauses."""

from time import sleep
import pytest
from pathlib import Path
from urllib.parse import urlparse

from polus.tools.workflows import (
    CommandLineTool,
    Workflow,
    StepBuilder,
    WorkflowBuilder,
    run_cwl,
)
from polus.tools.workflows.types import CWLArray, CWLBasicType, CWLBasicTypeEnum
from polus.tools.workflows.utils import configure_folders, file_exists

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)

PARAMS = [(["workflow3.cwl"], ["touch_single.cwl"])]
IDS = ["conditional-workflow"]


@pytest.fixture(params=PARAMS, ids=IDS)
def conditional_workflow(
    test_data_dir: Path, request: pytest.FixtureRequest
) -> Workflow:
    """Build a conditional workflow fixture."""

    workflows, clts = request.param

    steps = []

    # create the subworkflow step
    for filename in workflows:
        cwl_file = test_data_dir / filename
        clt = Workflow.load(cwl_file)
        step = StepBuilder()(clt)
        steps.append(step)

    # create the step with the conditional clause
    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        step = StepBuilder()(
            clt,
            when="$(inputs.should_execute < 1)",
            when_input_names=["should_execute"],
            add_inputs=[{"id": "should_execute", "type": "int"}],
        )
        steps.append(step)

    (echo_uppercase_wf, touch) = steps

    # linking steps
    touch.touchfiles = echo_uppercase_wf.uppercase_message

    # building full workflow
    wf = WorkflowBuilder(workdir=OUTPUT_DIR)("workflow_conditional", steps=steps)
    return wf


@pytest.mark.parametrize("filename", ["conditional-workflow.cwl"])
def test_load_conditional_wf(test_data_dir: Path, tmp_dir: Path, filename: str) -> None:
    """Test that we can load a workflow with a conditional step."""
    cwl_file = test_data_dir / filename
    wf = Workflow.load(cwl_file)
    wf.save(OUTPUT_DIR)
    wf.save(tmp_dir)

    assert len(wf.inputs) == 2
    assert len(wf.outputs) == 1

    wf_output = wf.outputs[0]
    assert isinstance(wf_output.type_, CWLArray)
    assert wf_output.type_.items == CWLBasicType(type=CWLBasicTypeEnum.FILE)

    wf_input_msg = wf.inputs[0]
    assert isinstance(wf_input_msg.type_, CWLArray)
    assert wf_input_msg.type_.items == CWLBasicType(type=CWLBasicTypeEnum.STRING)

    wf_input_should_touch = wf.inputs[1]
    assert wf_input_should_touch.type_ == CWLBasicType(type=CWLBasicTypeEnum.INT)

    # test last step has a when clause
    touch_step = wf.steps[-1]
    when_clause = touch_step.when
    assert when_clause
    # test the clause value
    assert when_clause == "$(inputs.should_execute < 1)"
    # check we do have a related workflow input
    assert wf_input_should_touch.id_ == "should_touch"
    assert touch_step.in_[0].source == wf_input_should_touch.id_


@pytest.mark.parametrize("filename", ["touch_single.cwl"])
def test_build_conditional_step(test_data_dir: Path, filename: str) -> None:
    """Test we can build a step with a conditional clause."""
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)

    step = StepBuilder()(
        clt,
        when="$(inputs.should_execute < 1)",
        when_input_names=["should_execute"],
        add_inputs=[{"id": "should_execute", "type": "int"}],
    )

    # Check that we added a new step input.
    assert len(clt.inputs) == 1
    assert len(step.in_) == 2

    # Check this step input has the correct name and type.
    additional_inputs = [input for input in step.in_ if input.id_ == "should_execute"]
    assert additional_inputs and len(additional_inputs) == 1
    should_execute = additional_inputs[0]
    assert should_execute.type_ == CWLBasicType(type=CWLBasicTypeEnum.INT)


def test_build_conditional_workflow(conditional_workflow: Workflow) -> None:
    """Test th workflow is correctly built."""

    input_count = len(conditional_workflow.inputs)
    expected_count = 2
    assert (
        input_count == expected_count
    ), f"workflow should have {expected_count} input, got {input_count}."

    wf_input_msg = conditional_workflow.inputs[0]
    assert wf_input_msg.type_ == CWLBasicType(type=CWLBasicTypeEnum.STRING)

    wf_input_should_execute = conditional_workflow.inputs[1]
    assert wf_input_should_execute.type_ == CWLBasicType(type=CWLBasicTypeEnum.INT)

    wf_output1 = conditional_workflow.outputs[0]
    assert wf_output1.type_ == CWLBasicType(type=CWLBasicTypeEnum.STRING)

    wf_output2 = conditional_workflow.outputs[1]
    assert wf_output2.type_ == CWLBasicType(type=CWLBasicTypeEnum.FILE)

    # test last step has a when clause
    touch_step = conditional_workflow.steps[-1]
    when_clause = touch_step.when
    assert when_clause
    # test the clause value
    assert when_clause == "$(inputs.should_execute < 1)"
    # check we do have a related workflow input
    assert touch_step.in_[1].id_ == "should_execute"
    assert (
        wf_input_should_execute.id_
        == "workflow_conditional___1__step__touch_single___should_execute"
    )
    assert touch_step.in_[1].source == wf_input_should_execute.id_


def test_run_positive(conditional_workflow: Workflow) -> None:
    """Run the conditonal workflow with manual configuration.

    Here the touch step is executed as the condition is true.
    The file is created.
    """
    wf_cwl_file = Path(urlparse(conditional_workflow.id_).path)

    filename = "message_file_created"
    input_names = [input.id_ for input in conditional_workflow.inputs]
    input_values = [f"--{input_names[0]}={filename}"]

    should_execute = 0
    input_values += [f"--{input_names[1]}={should_execute}"]
    run_cwl(wf_cwl_file, extra_args=input_values, cwd=STAGING_DIR)

    # TODO CHECK why we get those trailing \n
    path = Path(Path(STAGING_DIR / filename.upper()).as_posix() + "\n\n")

    # test existence
    file_exists(path)


def test_run_negative(conditional_workflow: Workflow) -> None:
    """Run the conditional workflow with manual configuration.

    Here the touch step is not executed as the condition is false.
    The file is not created.
    """
    # TODO add convenience method to grab the file from the model?
    wf_cwl_file = Path(urlparse(conditional_workflow.id_).path)
    filename = "message_file_never_created"
    input_names = [input.id_ for input in conditional_workflow.inputs]
    input_values = [f"--{input_names[0]}={filename}"]

    should_execute = 4
    input_values += [f"--{input_names[1]}={should_execute}"]
    run_cwl(wf_cwl_file, extra_args=input_values, cwd=STAGING_DIR)

    path = Path(Path(STAGING_DIR / filename.upper()).as_posix() + "\n\n")

    with pytest.raises(FileNotFoundError):
        file_exists(path)


def test_run_conditional_workflow_with_config(conditional_workflow: Workflow) -> None:
    """Run workflow with config file."""
    wf = StepBuilder()(conditional_workflow)
    wf.in_[0].value = "ok"
    wf.in_[1].value = 4

    conditional_workflow.save(OUTPUT_DIR)
    config = wf.save_config(OUTPUT_DIR)

    run_cwl(
        Path(OUTPUT_DIR) / f"{conditional_workflow.name}.cwl",
        config_file=config,
        cwd=STAGING_DIR,
    )
