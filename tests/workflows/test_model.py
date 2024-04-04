"""Test building parameters of various types."""

from polus.tools.workflows.model import Parameter
from polus.tools.workflows.types import CWLArray, CWLBasicType, CWLBasicTypeEnum


def test_parameter_cwl_complex_type_model() -> None:
    """Test creating a parameter of type array from CWLArray instance.

    The CWL Array is also created from a instance.
    """
    param_name = "input_array_string"
    type_ = CWLArray(items=CWLBasicType(type=CWLBasicTypeEnum.STRING))
    param = Parameter(id_=param_name, type=type_)

    assert param.id_ == param_name
    assert param.optional == False
    assert param.type_ == type_


def test_parameter_cwl_complex_type_raw() -> None:
    """Test creating a parameter of type array from CWLArray instance.

    The array is created from a dict.
    """
    param_name = "input_array_string"
    dict = {"type": "array", "items": "string"}
    type_ = CWLArray(**dict)  # build array from dcit
    param = Parameter(id_=param_name, type_=type_)

    param_type = CWLArray(items=CWLBasicType(type_=CWLBasicTypeEnum.STRING))
    assert param.id_ == param_name
    assert param.optional == False
    assert param.type_ == param_type


def test_parameter_cwl_complex_type_dump_model() -> None:
    """Test creating a parameter of type array from dict."""
    param_name = "input_array_string"
    dict = {"items": "string"}  # type is unecessary
    type_ = CWLArray(**dict)

    # use model dump to serialize array
    dict = {"id": param_name, "type": type_.model_dump()}
    param = Parameter(**dict)
    assert param.id_ == param_name
    assert param.optional == False
    assert param.type_ == type_


def test_parameter_cwl_base_type() -> None:
    "Test creating a param of type string."
    param_name = "input_string"
    type_ = CWLBasicType(type_=CWLBasicTypeEnum.STRING)
    dict = {"id": param_name, "type": type_}
    param = Parameter(**dict)

    assert param.id_ == param_name
    assert param.optional == False
    assert param.type_ == type_


def test_parameter_cwl_base_type_raw() -> None:
    "Test creating a param of type string."
    param_name = "input1"
    type_ = "string"
    dict = {"id": param_name, "type": type_}
    param = Parameter(**dict)

    param_type = CWLBasicType(type_=CWLBasicTypeEnum.STRING)
    assert param.id_ == param_name
    assert param.optional == False
    assert param.type_ == param_type


def test_parameter_serialization() -> None:
    """Test the serialization of a parameter."""
    param_name = "input1"
    type_ = CWLBasicType(type_=CWLBasicTypeEnum.STRING)
    # raw data
    dict = {"id": param_name, "type": type_}
    # create model and serialize
    param = Parameter(**dict)
    dict_out = param.model_dump(by_alias=True)

    # id is unchanged
    assert dict_out["id"] == param_name
    # type is serialized to its raw representation
    type_dict_out = "string"
    assert dict_out["type"] == type_dict_out
    # optional not serialized
    assert not "optional" in dict_out
