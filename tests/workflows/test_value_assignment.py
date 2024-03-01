"""Test value assignment."""

from pathlib import Path
from typing import Any

import pytest
from polus.tools.workflows.model import AssignableWorkflowStepInput
from polus.tools.workflows.types import CWLBasicType
from polus.tools.workflows.types import CWLBasicTypeEnum


@pytest.fixture()
def default_input_model() -> dict[Any, Any]:
    """Build a template AssignableWorkflowStepInput."""
    input_ = AssignableWorkflowStepInput(
        id="test_input",
        source="test_source",
        type="string",
        optional=True,
        step_id="test_step_id",
    )
    return input_.model_dump(by_alias=True)


def test_assign_int(default_input_model: dict[Any, Any]) -> None:
    """Test we can only assign an int."""
    type_dict = {"type": "int"}
    input_model = {**default_input_model, **type_dict, "optional": True}
    input_ = AssignableWorkflowStepInput(**input_model)

    # TODO CHECK optional is not serialize.
    # How can we still dump the raw model?
    # TODO review serialization to make this possible
    # TODO move to model test afterwards
    assert input_.type_ == CWLBasicType(type_=CWLBasicTypeEnum.INT)

    assert input_.type_.is_value_assignable(
        4,
    ), f"Was expecting a int, got {input_.type_}"
    assert not input_.type_.is_value_assignable("ok")


def test_assign_string(default_input_model: dict[Any, Any]) -> None:
    """Test we can only assign an string."""
    type_dict = {"type": "string"}
    input_model = {**default_input_model, **type_dict, "optional": True}
    input_ = AssignableWorkflowStepInput(**input_model)

    assert input_.type_.is_value_assignable(
        "ok",
    ), f"Was expecting a int, got {input_.type_}"
    assert not input_.type_.is_value_assignable(4)


def test_assign_array_of_strings(default_input_model: dict[Any, Any]) -> None:
    """Test we can only assign an array of strings."""
    type_dict = {"type": {"type": "array", "items": "string"}}
    input_model = {**default_input_model, **type_dict, "optional": True}
    input_ = AssignableWorkflowStepInput(**input_model)

    assert input_.type_.is_value_assignable(["ok"])
    assert input_.type_.is_value_assignable(["ok1", "ok2"])
    assert not input_.type_.is_value_assignable(
        ["ok", 4],
    )  # cannot mix strings and ints


def test_assign_array_of_files(default_input_model: dict[Any, Any]) -> None:
    """Test we can only assign an array of paths."""
    type_dict = {"type": {"type": "array", "items": "File"}}
    input_model = {**default_input_model, **type_dict, "optional": True}
    input_ = AssignableWorkflowStepInput(**input_model)

    assert input_.type_.is_value_assignable(
        [Path("path/to/file1", Path("path/to/file2"))],
    )


def test_assign_nested_array(default_input_model: dict[Any, Any]) -> None:
    """Test we can only assign a nested array."""
    type_dict = {
        "type": {"type": "array", "items": {"type": "array", "items": "string"}},
    }
    input_model = {**default_input_model, **type_dict, "optional": True}
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
