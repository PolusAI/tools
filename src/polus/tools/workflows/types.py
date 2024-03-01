"""CWl Types."""

import abc
from enum import Enum
from pathlib import Path
from typing import Annotated
from typing import Any
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import BeforeValidator
from pydantic import ConfigDict
from pydantic import Field
from pydantic import SerializerFunctionWrapHandler
from pydantic import WrapSerializer

PythonValue = Any
CWLValue = Union[dict, list, PythonValue]


class CWLBaseType(BaseModel, metaclass=abc.ABCMeta):
    """Base Model for all CWL Types."""

    @abc.abstractmethod
    def is_value_assignable(self, value: PythonValue) -> bool:
        """Check if a python value is assignable to this type."""
        pass

    @abc.abstractmethod
    def serialize_value(self, value: PythonValue) -> CWLValue:
        """Serialize a python value according CWL standard."""
        pass


def process_type(type_: Any) -> "CWLType":  # noqa: ANN401
    """Factory for the concrete type."""
    if isinstance(type_, str):
        return CWLBasicType(type=type_)
    if isinstance(type_, dict):
        return CWLArray(**type_)
    return type_


# TODO check if we should make use of nxt
def serialize_type(
    type_: "CWLType",
    nxt: Optional[SerializerFunctionWrapHandler] = None,  # noqa
) -> Union[dict, str]:
    """Serialize CWLTypes based on actual type."""
    if isinstance(type_, CWLBasicType):
        return type_.type_.value
    return {"type": "array", "items": serialize_type(type_.items)}


# Representation of any cwltypes.
CWLType = Annotated[
    CWLBaseType,
    BeforeValidator(process_type),
    WrapSerializer(serialize_type),
]


class CWLArray(CWLBaseType):
    """Model that represents a CWL Array."""

    model_config = ConfigDict(populate_by_name=True)

    type_: str = Field("array", alias="type")
    items: CWLType

    def is_value_assignable(self, value: PythonValue) -> bool:
        """Check that the python variable type can be assigned to this cwl type."""
        if not isinstance(value, list):
            return False
        # we check every array element.
        return all(self.items.is_value_assignable(item) for item in value)

    def serialize_value(self, value: PythonValue) -> CWLValue:
        """Serialize input values."""
        return [self.items.serialize_value(val) for val in value]


class CWLBasicTypeEnum(Enum):
    """CWL basic types."""

    NULL = "null"
    BOOLEAN = "boolean"
    INT = "int"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"
    FILE = "File"
    DIRECTORY = "Directory"

    def is_value_assignable(self, value: PythonValue) -> bool:
        """Check if the python variable type can be assigned to this cwl type."""
        if self == CWLBasicTypeEnum.STRING:
            return isinstance(value, str)
        if self == CWLBasicTypeEnum.INT or self == CWLBasicTypeEnum.LONG:
            return isinstance(value, int)
        if self == CWLBasicTypeEnum.FLOAT or self == CWLBasicTypeEnum.DOUBLE:
            return isinstance(value, float)
        if self == CWLBasicTypeEnum.FILE or self == CWLBasicTypeEnum.DIRECTORY:
            return isinstance(value, Path)
        if self == CWLBasicTypeEnum.BOOLEAN:
            return isinstance(value, bool)
        return False

    def serialize_value(self, value: PythonValue) -> CWLValue:
        """Serialize input values."""
        if self == CWLBasicTypeEnum.DIRECTORY:
            return {"class": "Directory", "location": Path(value).as_posix()}
        if self == CWLBasicTypeEnum.FILE:
            return {"class": "File", "location": Path(value).as_posix()}
        return value


class CWLBasicType(CWLBaseType):
    """Model that wraps an enum representing the basic types."""

    model_config = ConfigDict(populate_by_name=True)

    type_: CWLBasicTypeEnum = Field(..., alias="type")

    def is_value_assignable(self, value: PythonValue) -> bool:
        """Check if the given value is represented by this type."""
        return self.type_.is_value_assignable(value)

    def serialize_value(self, value: PythonValue) -> CWLValue:
        """Serialize input values."""
        return self.type_.serialize_value(value)
