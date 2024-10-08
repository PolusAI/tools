"""Contains the less commonly used part of the model."""

from enum import Enum
from typing import Any
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from polus.tools.workflows.requirements import ProcessRequirement
from polus.tools.workflows.types import Expression


class ScatterMethodEnum(str, Enum):
    """Options for scatterMethod.

    https://www.commonwl.org/v1.2/Workflow.html#Scatter/gather
    """

    dotproduct = "dotproduct"
    nested_crossproduct = "nested_crossproduct"
    flat_crossproduct = "flat_crossproduct"


class LoadListingEnum(str, Enum):
    """Desired behavior for loading listing.

    https://www.commonwl.org/v1.2/Workflow.html#LoadListingEnum
    """

    no_listing = "no_listing"
    shallow_listing = "shallow_listing"
    deep_listing = "deep_listing"


class LinkMergeMethod(str, Enum):
    """Input link merge method.

    https://www.commonwl.org/v1.2/Workflow.html#Merging_multiple_inbound_data_links
    """

    merge_nested = "merge_nested"
    merge_flattened = "merge_flattened"


class PickValueMethod(str, Enum):
    """Picking non-null values among inbound data links.

    https://www.commonwl.org/v1.2/Workflow.html#Picking_non-null_values_among_inbound_data_links
    """

    first_non_null = "first_non_null"
    the_only_non_null = "the_only_non_null"
    all_non_null = "all_non_null"


class CwlRootObject(BaseModel):
    """Metadata found in root objects.

    See https://www.commonwl.org/v1.2/SchemaSalad.html#Explicit_context
    """

    base: Optional[str] = Field(None, alias="$base")
    namespaces: Optional[dict[str, str]] = Field(None, alias="$namespaces")
    schemas: Optional[list[str]] = Field(None, alias="$schemas")

    graph: Optional[list] = Field(None, alias="$graph")


class CwlDocExtra(BaseModel):
    """Extra Model properties for documentation."""

    doc: Optional[Union[str, list[str]]] = None
    label: Optional[str] = None


class CwlRequireExtra(BaseModel):
    """Extra model properties for requirements."""

    requirements: Optional[list[ProcessRequirement]] = None
    hints: Optional[list[Any]] = None


class SecondaryFileSchema(BaseModel):
    """SecondaryFileSchema."""

    pattern: Union[str, Expression]
    required: Optional[Union[bool, Expression]] = None


class CommandOutputRecordSchema(BaseModel):
    """CommandOutputRecordSchema."""

    pass


class CommandOutputRecordField(BaseModel):
    """CommandOutputRecordField."""

    pass


class InputBinding(BaseModel):
    """Base class for any Input Binding."""

    load_contents: Optional[bool] = Field(None, alias="loadContents")


class CommandInputRecordField(CwlDocExtra):
    """CommandInputRecordField."""

    name: str
    type_: Any = Field(
        ...,
        alias="type",
    )  # NOTE we would need to implement the last cwl types
    secondary_files: Optional[
        Union[SecondaryFileSchema, list[SecondaryFileSchema]]
    ] = Field(None, alias="secondaryFiles")
    streamable: Optional[bool] = None
    format_: Optional[Union[str, list[str], Expression]] = Field(None, alias="format")
    load_contents: Optional[bool] = Field(None, alias="loadContents")
    load_listing: Optional[LoadListingEnum] = Field(None, alias="loadListing")
    input_binding: Optional[InputBinding] = Field(None, alias="inputBinding")


class CommandInputRecordSchema(CwlDocExtra):
    """CommandInputRecordSchema."""

    type_: str = Field("record", alias="type")
    fields: Optional[list[CommandInputRecordField]] = None
    name: Optional[str] = None
    input_binding: Optional[InputBinding] = Field(None, alias="inputBinding")


class CommandLineBinding(InputBinding):
    """CommandLineBinding.

    Describe how to translate the input parameter to a
    program argument.
    """

    model_config = ConfigDict(populate_by_name=True)

    load_contents: Optional[bool] = Field(None, alias="loadContents")
    position: Optional[int] = None
    prefix: Optional[str] = Field(None)
    separate: Optional[bool] = Field(None)
    item_separator: Optional[str] = Field(None, alias="ItemSeparator")
    value_from: Optional[Union[str, Expression]] = Field(None, alias="valueFrom")
    shell_quote: Optional[bool] = Field(None, alias="ShellQuote")


class CommandOutputBinding(BaseModel):
    """CommandOutputBinding.

    Describe how to translate the wrapped program result
    into a an output parameter.
    """

    model_config = ConfigDict(populate_by_name=True)

    load_contents: Optional[bool] = Field(None, alias="loadContents")
    load_listing: Optional[LoadListingEnum] = Field(None, alias="loadListing")
    glob: Optional[Union[str, list[str], Expression]] = None
    output_eval: Optional[Expression] = Field(None, alias="outputEval")
