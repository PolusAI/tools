"""Test value assignment."""

from pathlib import Path

import pytest
from polus.tools.workflows.builders import StepBuilder
from polus.tools.workflows.model import AssignableWorkflowStepInput
from polus.tools.workflows.model import Process
from polus.tools.workflows.types import CWLBasicType
from polus.tools.workflows.types import CWLBasicTypeEnum


@pytest.fixture()
def default_input_model() -> dict:
    """Build a template AssignableWorkflowStepInput."""
    input_ = AssignableWorkflowStepInput(
        id="test_input",
        source="test_source",
        type="string",
        optional=True,
        step_id="test_step_id",
    )
    return input_.model_dump(by_alias=True)


def test_assign_int(default_input_model: dict) -> None:
    """Test we can only assign an int."""
    type_dict = {"type": "int"}
    input_model = {
        **default_input_model,
        **type_dict,
        "optional": True,
        "step_id": "test_step_id",
    }
    input_ = AssignableWorkflowStepInput(**input_model)

    assert input_.type_ == CWLBasicType(type_=CWLBasicTypeEnum.INT)
    assert input_.type_.is_value_assignable(
        4,
    ), f"Was expecting a int, got {input_.type_}"
    assert not input_.type_.is_value_assignable("ok")


def test_assign_string(default_input_model: dict) -> None:
    """Test we can only assign an string."""
    type_dict = {"type": "string"}
    input_model = {
        **default_input_model,
        **type_dict,
        "optional": True,
        "step_id": "test_step_id",
    }
    input_ = AssignableWorkflowStepInput(**input_model)

    assert input_.type_.is_value_assignable(
        "ok",
    ), f"Was expecting a int, got {input_.type_}"
    assert not input_.type_.is_value_assignable(4)


def test_assign_array_of_strings(default_input_model: dict) -> None:
    """Test we can only assign an array of strings."""
    type_dict = {"type": {"type": "array", "items": "string"}}
    input_model = {
        **default_input_model,
        **type_dict,
        "optional": True,
        "step_id": "test_step_id",
    }
    input_ = AssignableWorkflowStepInput(**input_model)

    assert input_.type_.is_value_assignable(["ok"])
    assert input_.type_.is_value_assignable(["ok1", "ok2"])
    assert not input_.type_.is_value_assignable(
        ["ok", 4],
    )  # cannot mix strings and ints


def test_assign_array_of_files(default_input_model: dict) -> None:
    """Test we can only assign an array of paths."""
    type_dict = {"type": {"type": "array", "items": "File"}}
    input_model = {
        **default_input_model,
        **type_dict,
        "optional": True,
        "step_id": "test_step_id",
    }
    input_ = AssignableWorkflowStepInput(**input_model)

    assert input_.type_.is_value_assignable(
        [Path("path/to/file1", Path("path/to/file2"))],
    )


def test_assign_nested_array(default_input_model: dict) -> None:
    """Test we can only assign a nested array."""
    type_dict = {
        "type": {"type": "array", "items": {"type": "array", "items": "string"}},
    }
    input_model = {
        **default_input_model,
        **type_dict,
        "optional": True,
        "step_id": "test_step_id",
    }
    input_ = AssignableWorkflowStepInput(**input_model)

    assert input_.type_.is_value_assignable([["ok"]])  # nested array of strings ok
    assert input_.type_.is_value_assignable(
        [["ok1"], ["ok2"]],
    )  # nested array of strings ok
    assert not input_.type_.is_value_assignable([[4]])  # nested array of int not ok
    assert not input_.type_.is_value_assignable([4])  # simple array not ok
    assert not input_.type_.is_value_assignable(
        [[["ok"]]],
    )  # deeper array nesting not ok
    assert not input_.type_.is_value_assignable(
        [["ok"], [4]],
    )  # cannot mix and match types.


@pytest.mark.parametrize("filename", ["uppercase2_wic_compatible2.cwl"])
def test_input_output_with_same_names(test_data_dir: Path, filename: str) -> None:
    """Test assigning and getting inputs and outputs with the same name.

    Test and document how this case is handled.
    """
    cwl_file = test_data_dir / filename
    clt = Process.load(cwl_file)
    step = StepBuilder()(clt)

    value_set = "hello"
    step.uppercase_message = (
        value_set  # set will use input since assigning output is forbidden.
    )

    # since we have an input / output with the same name,
    # we return the a tuple with both.
    (uppercase_message_input, uppercase_message_output) = step.uppercase_message
    assert (
        uppercase_message_input.value == value_set
    ), f"expected {value_set}, got {uppercase_message_input.value}"
    assert (
        uppercase_message_output.value is None
    ), f"expected None, got {uppercase_message_output.value}"
