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
from polus.tools.workflows.exceptions import ScatterValidationError
from polus.tools.workflows.model import ScatterMethodEnum
from polus.tools.workflows.types import CWLArray, CWLBasicType, CWLBasicTypeEnum
from polus.tools.workflows.utils import configure_folders

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)

PARAMS = [([], ["echo_string.cwl", "uppercase2_wic_compatible3.cwl"])]
IDS = ["scatter-workflow"]


@pytest.fixture(params=PARAMS, ids=IDS)
def scatter_workflow(test_data_dir: Path, request: pytest.FixtureRequest) -> Workflow:
    """Build a conditional workflow fixture."""

    _, clt_files = request.param
    clts = []
    for filename in clt_files:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        clts.append(clt)

    (echo, uppercase) = clts

    # scatter all inputs for echo
    scattered_inputs = [input_.id_ for input_ in echo.inputs]
    step1 = StepBuilder()(echo, scatter=scattered_inputs)

    # scatter all inputs for uppercase
    scattered_inputs = [input_.id_ for input_ in uppercase.inputs]
    step2 = StepBuilder()(uppercase, scatter=scattered_inputs)

    # linking scattered steps
    step2.message = step1.message_string

    wf_builder = WorkflowBuilder(workdir=OUTPUT_DIR)
    wf = wf_builder("wf_scatter", steps=[step1, step2])

    assert len(wf.inputs) == 1
    assert len(wf.outputs) == 2

    # Check the workflow input has been correctly promoted to array of string.
    wf_input_0 = wf.inputs[0]
    assert isinstance(wf_input_0.type_, CWLArray)
    assert wf_input_0.type_.items == CWLBasicType(type=CWLBasicTypeEnum.STRING)

    # Check the workflow outputs have been correctly promoted to array of string.
    for wf_output in wf.outputs:
        assert isinstance(wf_output.type_, CWLArray)
        assert wf_output.type_.items == CWLBasicType(type=CWLBasicTypeEnum.STRING)

    return wf


@pytest.mark.parametrize("filename", ["scatter-workflow2.cwl"])
def test_load_scatter_wf(test_data_dir: Path, tmp_dir: Path, filename: str) -> None:
    """Test that we can load  a workflow with ScatterFeatureRequirement."""

    cwl_file = test_data_dir / filename
    scatter_wf = Workflow.load(cwl_file)
    scatter_wf.save(OUTPUT_DIR)
    scatter_wf.save(tmp_dir)

    assert len(scatter_wf.inputs) == 1
    assert len(scatter_wf.outputs) == 1

    wf_output = scatter_wf.outputs[0]
    assert isinstance(wf_output.type_, CWLArray)
    assert wf_output.type_.items.type_ == CWLBasicTypeEnum.FILE

    wf_input = scatter_wf.inputs[0]
    assert isinstance(wf_input.type_, CWLArray)
    assert wf_input.type_.items.type_ == CWLBasicTypeEnum.STRING

    # Check we do have a scatter feature requirement
    assert "ScatterFeatureRequirement" in set(
        [req.class_ for req in scatter_wf.requirements]
    )


@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_build_scatter_step(test_data_dir: Path, filename: str) -> None:
    """Test we can build a step with scattered inputs.

    In particular, check that type promotion is properly handled.
    """

    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    step1 = StepBuilder()(clt)

    assert len(step1.in_) == 1
    assert len(step1.out) == 1

    # type checks
    assert step1.message.type_ == CWLBasicType(type=CWLBasicTypeEnum.STRING)
    assert step1.message_string.type_ == CWLBasicType(type=CWLBasicTypeEnum.STRING)

    # check value assignment
    step1.message = "test_message"

    # build a scatter step
    scattered_inputs = [input_.id_ for input_ in clt.inputs]
    step1 = StepBuilder()(clt, scatter=scattered_inputs)

    assert len(step1.in_) == 1
    assert len(step1.out) == 1

    # type promotion on scatter
    assert isinstance(step1.message.type_, CWLArray)
    assert step1.message.type_.items == CWLBasicType(type=CWLBasicTypeEnum.STRING)
    assert isinstance(step1.message_string.type_, CWLArray)
    assert step1.message_string.type_.items == CWLBasicType(
        type=CWLBasicTypeEnum.STRING
    )

    # check we can assign a array now
    step1.message = ["test_message"]


@pytest.mark.parametrize("filename", ["echo_string_array.cwl"])
def test_build_scatter_step_nested_array(test_data_dir: Path, filename: str) -> None:
    """Test we can build a step with scattered inputs
    over array types."""

    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    step1 = StepBuilder()(clt)

    assert len(step1.in_) == 1
    assert len(step1.out) == 1

    # type checks
    assert step1.message.type_ == CWLArray(
        items=CWLBasicType(type=CWLBasicTypeEnum.STRING)
    )
    assert step1.message_string.type_ == CWLArray(
        items=CWLBasicType(type=CWLBasicTypeEnum.STRING)
    )

    # check value assignment
    step1.message = ["test_message1", "test_message2"]

    # build a scatter step
    scattered_inputs = [input_.id_ for input_ in clt.inputs]
    step1 = StepBuilder()(clt, scatter=scattered_inputs)

    assert len(step1.in_) == 1
    assert len(step1.out) == 1

    # Check we have a nested array
    assert step1.message.type_ == CWLArray(
        items=CWLArray(items=CWLBasicType(type=CWLBasicTypeEnum.STRING))
    )

    # We can assign nested arrays.
    step1.message = [["ok1", "ok2"]]


@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_scatter_over_bad_inputs(test_data_dir: Path, filename: str) -> None:
    """Test that properly report exception if scatter contains
    non-existing input names.
    """

    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    scattered_inputs = [input_.id_ for input_ in clt.inputs]
    scattered_inputs.append("nonExistingInput")

    with pytest.raises(ScatterValidationError):
        StepBuilder()(clt, scatter=scattered_inputs)


@pytest.mark.parametrize("filename", ["uppercase2_wic_compatible2.cwl"])
def test_scatter_add_scatter_method(test_data_dir: Path, filename: str) -> None:
    """Test that we create a scatter method if required and missing."""
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    scattered_inputs = [input_.id_ for input_ in clt.inputs]
    step = StepBuilder()(clt, scatter=scattered_inputs)

    assert step.scatter_method == ScatterMethodEnum.dotproduct


def test_run_scatter_wf(scatter_workflow: Workflow, tmp_dir: Path):
    """Test we can run a workflow with linked scattered steps.

    In particular, check that type promotion is properly handled.
    """

    wf_cwl_file = Path(urlparse(scatter_workflow.id_).path)
    input_names = [input_.id_ for input_ in scatter_workflow.inputs]
    input_values = [f"--{input_names[0]}=test_message{i}" for i in range(4)]
    run_cwl(wf_cwl_file, extra_args=input_values, cwd=STAGING_DIR)


def test_run_scatter_wf_with_config(scatter_workflow: Workflow, tmp_dir: Path) -> None:
    """Test we can run a workflow with linked scattered steps.

    In particular, check that type promotion is properly handled.
    """
    scatter_workflow.save(OUTPUT_DIR)
    wf_step = StepBuilder()(scatter_workflow)
    wf_step.in_[0].value = ["test_message1", "test_message2"]
    config = wf_step.save_config(path=OUTPUT_DIR)
    run_cwl(
        STAGING_DIR / f"{scatter_workflow.name}.cwl",
        config_file=config,
        cwd=STAGING_DIR,
    )
