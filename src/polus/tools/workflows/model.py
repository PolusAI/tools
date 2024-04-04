"""The main cwl models."""

from collections.abc import KeysView
from pathlib import Path
from typing import Annotated
from typing import Any
from typing import Optional
from typing import Union

import cwl_utils.parser as cwl_parser
import yaml  # type: ignore[import]
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import SerializerFunctionWrapHandler
from pydantic import WrapSerializer
from pydantic import field_serializer
from pydantic import model_serializer
from pydantic import model_validator
from pydantic.functional_validators import field_validator
from schema_salad.exceptions import ValidationException as CwlParserException
from typing_extensions import Self

import polus.tools.workflows.builders
from polus.tools.workflows.default_ids import extract_name_from_id
from polus.tools.workflows.default_ids import generate_cwl_source_repr
from polus.tools.workflows.exceptions import BadCwlProcessFileError
from polus.tools.workflows.exceptions import IncompatibleTypeError
from polus.tools.workflows.exceptions import IncompatibleValueError
from polus.tools.workflows.exceptions import InvalidFormatError
from polus.tools.workflows.exceptions import OutputAssignmentError
from polus.tools.workflows.exceptions import ScatterValidationError
from polus.tools.workflows.exceptions import UnexpectedClassError
from polus.tools.workflows.exceptions import UnexpectedTypeError
from polus.tools.workflows.exceptions import UnsupportedProcessClassError
from polus.tools.workflows.logger import get_logger
from polus.tools.workflows.model_extra import CommandLineBinding
from polus.tools.workflows.model_extra import CommandOutputBinding
from polus.tools.workflows.model_extra import CwlDocExtra
from polus.tools.workflows.model_extra import CwlRequireExtra
from polus.tools.workflows.model_extra import CwlRootObject
from polus.tools.workflows.model_extra import LinkMergeMethod
from polus.tools.workflows.model_extra import LoadListingEnum
from polus.tools.workflows.model_extra import PickValueMethod
from polus.tools.workflows.model_extra import ScatterMethodEnum
from polus.tools.workflows.model_extra import SecondaryFileSchema
from polus.tools.workflows.types import CWLArray
from polus.tools.workflows.types import CWLBasicType
from polus.tools.workflows.types import CWLBasicTypeEnum
from polus.tools.workflows.types import CWLType
from polus.tools.workflows.types import CWLValue
from polus.tools.workflows.types import Expression
from polus.tools.workflows.types import PythonValue
from polus.tools.workflows.types import SerializedModel
from polus.tools.workflows.utils import directory_exists
from polus.tools.workflows.utils import file_exists

logger = get_logger(__name__)


def is_valid_parameter_id(id_: str) -> str:
    """Check if parameter id is valid."""
    # Check for specific guidelines in the spec.
    return id_


ParameterId = Annotated[str, [is_valid_parameter_id]]


class Parameter(CwlDocExtra):
    """Parameter.

    Base representation of any parameters.
    Every parameter must have an id and a type.
    We also track if the parameter is optional or not
    (CWL encodes this information in the type declaration).
    """

    model_config = ConfigDict(populate_by_name=True)

    id_: ParameterId = Field(..., alias="id")
    type_: CWLType = Field(..., alias="type")
    optional: bool = Field(False, exclude=True)
    format_: Optional[Union[str, list[str], Expression]] = Field(None, alias="format")

    secondary_files: Optional[
        Union[SecondaryFileSchema, list[SecondaryFileSchema]]
    ] = Field(None, alias="secondaryFiles")
    streamable: Optional[bool] = None

    @model_validator(mode="before")
    def transform_type(self) -> Self:
        """Check if we have an optional type."""
        # we allow attribute name or alias so fold both cases.
        key = "type_" if self.get("type_") else "type"

        if isinstance(self[key], list):
            # optional types are implemented as list
            # with first element set to null
            if self[key][0] == "null":
                self["optional"] = True
                self[key] = self[key][1]
            else:
                raise UnexpectedTypeError(self[key])
        return self

    @model_validator(mode="after")
    def verify_format(self) -> Self:
        """Check that format field is allowed."""
        if self.format_:
            if self.type_ == CWLBasicType(
                type_=CWLBasicTypeEnum.FILE,
            ) or self.type_ == CWLArray(
                items=CWLBasicType(type_=CWLBasicTypeEnum.FILE),
            ):
                return self
            msg = "format only allowed with File or array of File."
            raise InvalidFormatError(msg)
        return self

    @model_serializer(mode="wrap", when_used="always")
    def serialize_model(self, nxt: Any) -> SerializedModel:  # noqa ANN401
        """When serializing, add optional info in the type."""
        # NOTE here we favor syntactic sugar for simple types.
        if self.optional:
            add_trailing_question_mark = False
            if isinstance(self.type_, CWLBasicType):
                add_trailing_question_mark = True
            # NOTE Only valid if we used syntactic sugar for simple arrays.
            if isinstance(self.type_, CWLArray) and isinstance(
                self.type_.items,
                CWLBasicType,
            ):
                add_trailing_question_mark = True

        serialized = nxt(self)

        if self.optional:
            if add_trailing_question_mark:
                serialized["type"] = str(serialized["type"]) + "?"
            else:
                serialized["type"] = ["null", serialized["type"]]
        return serialized


class InputParameter(Parameter):
    """Base class of any input parameter."""

    model_config = ConfigDict(populate_by_name=True)

    input_binding: Optional[CommandLineBinding] = Field(None, alias="inputBinding")
    load_contents: Optional[bool] = Field(None, alias="loadContents")
    load_listing: Optional[LoadListingEnum] = Field(None, alias="loadListing")
    default: Optional[CWLValue] = None


class OutputParameter(Parameter):
    """Base class of any input parameter."""


class WorkflowInputParameter(InputParameter):
    """WorkflowInputParameter.

    Workflow input parameters define how what inputs
    to provide to execute a workflow.
    """

    pass


class WorkflowOutputParameter(OutputParameter):
    """WorkflowOutputParameter.

    Workflow output parameters define how to collect
    the outputs of a workflow.

    Args:
    - outputSource: ref to the WorkflowStepOutput
    this workflow output is linked to.
    """

    model_config = ConfigDict(populate_by_name=True)

    output_source: str = Field(..., alias="outputSource")
    link_merge: Optional[PickValueMethod] = Field(None, alias="linkMerge")
    pick_value: Optional[PickValueMethod] = Field(None, alias="pickValue")


class CommandInputParameter(InputParameter):
    """Command Line Tool input parameter."""


class CommandOutputParameter(OutputParameter):
    """Command Line Tool output parameter."""

    model_config = ConfigDict(populate_by_name=True)

    output_binding: Optional[CommandOutputBinding] = Field(None, alias="outputBinding")


def is_valid_stepio_id(id_: str) -> str:
    """Check if we have a valid step input/output io id."""
    return id_


StepIOId = Annotated[str, [is_valid_stepio_id]]


class WorkflowStepOutput(BaseModel):
    """WorkflowStepOuput.

    WorkflowStepOuput define the name of a step output that can be used
    as a reference in another step input or a workflow output.
    """

    model_config = ConfigDict(populate_by_name=True)

    id_: StepIOId = Field(..., alias="id")


class AssignableWorkflowStepOutput(WorkflowStepOutput):
    """AssignableWorkflowStepOutput.

    This a special kind of WorkflowStepOutput that can
    be dynamically link to another step input.
    """

    model_config = ConfigDict(populate_by_name=True)

    type_: CWLType = Field(..., exclude=True, alias="type")
    format_: Optional[Union[str, list[str], Expression]] = Field(
        None,
        exclude=True,
        alias="format",
    )
    value: PythonValue = Field(None, exclude=True)
    step_id: str = Field(..., exclude=True)


class WorkflowStepInput(CwlDocExtra):
    """WorkflowStepInput.

    It describes how to provide an input to a workflow step.
    It provides a ref to a workflow input or another step output.
    """

    model_config = ConfigDict(populate_by_name=True)

    id_: StepIOId = Field(..., alias="id")
    source: Optional[Union[str, list[str]]]

    link_merge: Optional[LinkMergeMethod] = Field(None, alias="linkMerge")
    pick_value: Optional[PickValueMethod] = Field(None, alias="pickValue")
    load_contents: Optional[bool] = Field(None, alias="loadContents")
    load_listing: Optional[LoadListingEnum] = Field(None, alias="loadListing")
    value_from: Optional[Union[str, Expression]] = Field(None, alias="valueFrom")


class AssignableWorkflowStepInput(WorkflowStepInput):
    """AssignableWorkflowStepInput.

    This a special kind of WorkflowStepInput that can
    have values assigned to or can be linked to another
    workflow input or step output.
    """

    model_config = ConfigDict(populate_by_name=True)

    type_: CWLType = Field(exclude=True, alias="type")
    optional: bool = Field(exclude=True)
    format_: Optional[Union[str, list[str], Expression]] = Field(
        None,
        exclude=True,
        alias="format",
    )
    value: PythonValue = Field(None, exclude=True)
    step_id: str = Field(..., exclude=True)

    def set_value(
        self,
        value: Union[PythonValue, AssignableWorkflowStepOutput],
    ) -> None:
        """Assign a value to this step input or link it to another step output."""
        if isinstance(value, tuple):
            value = value[1]  # we can assign outputs to inputs.

        if isinstance(value, AssignableWorkflowStepOutput):
            if self.type_ != value.type_:
                raise IncompatibleTypeError(self.type_, value.type_)
            self.check_format(value)
            source = generate_cwl_source_repr(value.step_id, value.id_)
            return super().__setattr__("source", source)

        if isinstance(value, list):
            multi_inputs = False
            for val in value:
                if multi_inputs and not isinstance(val, AssignableWorkflowStepOutput):
                    raise IncompatibleValueError(self.id_, self.type_, value)
                if isinstance(val, AssignableWorkflowStepOutput):
                    multi_inputs = True
            if multi_inputs:
                multiple_sources = []
                for val in value:
                    if self.type_ != CWLArray(items=val.type_):
                        raise IncompatibleTypeError(self.type_, val.type_)
                    self.check_format(val)
                    multiple_sources.append(
                        generate_cwl_source_repr(val.step_id, val.id_),
                    )
                return super().__setattr__("source", multiple_sources)

        if value is not None and not self.type_.is_value_assignable(value):
            raise IncompatibleValueError(self.id_, self.type_, value)
        return super().__setattr__("value", value)

    def check_format(self: Self, value: AssignableWorkflowStepOutput) -> None:
        """Check that formats are compatible."""
        if self.format_ and value.format_ and self.format_ != value.format_:
            # NOTE for now we just warn if formats are not equivalent.
            # we could do more advanced reasoning with ontologies if necessary.
            # We can the namespace using $namespaces.
            logger.warning(
                f"assigning output: {value.id_} to input: {self.id_}."
                f"formats do not match. Got {self.format_} and {value.format_}",
            )

    def __setattr__(
        self,
        name: str,
        value: Union[PythonValue, AssignableWorkflowStepOutput],
    ) -> None:
        """This is enabling assignment in our python DSL.

        This method specifically allow us to assign values to input directly,
        using this notation `step.in_[1].value = value`
        """
        if name == "value":
            self.set_value(value)
            return None
        return super().__setattr__(name, value)


def check_valid_workflow_step_id(id_: str) -> str:
    """Check if we have a valid workflow step id."""
    # NOTE we could try to fix it or throw an error.
    return id_.replace("-", "_")


WorkflowStepId = Annotated[str, [check_valid_workflow_step_id]]


def filter_unused_optional(
    in_: list[WorkflowStepInput],
    nxt: SerializerFunctionWrapHandler,
) -> list[dict]:
    """When serializing the model, ignore unused optional inputs.

    It seems that CWL does not have a construct for unset values.
    Trying to pass unset inputs will result in a cwl failure, so
    we need to strip them out.
    """
    filtered_in_ = [input_ for input_ in in_ if input_.source is not None]
    return nxt(filtered_in_)


# represents step inputs
WorkflowStepInputs = Annotated[
    list[WorkflowStepInput],
    WrapSerializer(filter_unused_optional),
]

# represents step outputs
WorkflowStepOutputs = Annotated[list[WorkflowStepOutput], []]


class WorkflowStep(CwlDocExtra, CwlRequireExtra):
    """Capture a workflow step.

    A workflow step has an id so it can be referenced by other steps,
    or workflow ios.
    It has a list of inputs whose ids correspond to the process input ids they
    are wrapping and describe to which workflow input/step outputs they connect.
    It has a list of outputs whose ids correspond to the process output ids they
    are wrapping and describe to  which workflow inputs they connect.
    """

    model_config = ConfigDict(populate_by_name=True)

    id_: WorkflowStepId = Field(..., alias="id")
    run: Union[str, "Process"]
    in_: WorkflowStepInputs = Field(..., alias="in")
    out: WorkflowStepOutputs = Field(...)
    when: Optional[Expression] = Field(None)  # ref to conditional execution clauses
    scatter: Optional[list[str]] = Field(None)  # ref to scatter inputs
    scatter_method: Optional[ScatterMethodEnum] = Field(None, alias="scatterMethod")
    from_builder: Optional[bool] = Field(False, exclude=True)

    @property
    def _inputs(self) -> dict[StepIOId, WorkflowStepInput]:
        """Generate a dict of WorkflowStepInputs for efficient retrieval."""
        return {input_.id_: input_ for input_ in self.in_}

    @property
    def _outputs(self) -> dict[StepIOId, WorkflowStepOutput]:
        """Generate a dict of WorkflowStepOutputs for efficient retrieval."""
        return {output.id_: output for output in self.out}

    @field_serializer("scatter_method", when_used="always")
    @classmethod
    def serialize_scatter_method(cls, scatter_method: ScatterMethodEnum) -> str:
        """When serializing, return only the list of ids."""
        return scatter_method.value

    @field_serializer("out", when_used="always")
    @classmethod
    def serialize_workflow_step_outputs(cls, out: WorkflowStepOutputs) -> list[str]:
        """When serializing, return only the list of ids."""
        return [output.id_ for output in out]

    @field_validator("out", mode="before")
    @classmethod
    def preprocess_workflow_step_outputs(
        cls,
        out: list[Union[str, dict[str, str]]],
    ) -> list[dict[str, str]]:
        """Wrap ids if we receive them as simple strings.

        This is required when loading a workflow with the cwl parser.
        """
        return [
            {"id": wf_step_output}
            if isinstance(wf_step_output, str)
            else wf_step_output
            for wf_step_output in out
        ]

    @field_validator("scatter", mode="before")
    @classmethod
    def preprocess_scatter(cls, scatter: Union[str, list]) -> list:
        """Preprocess scatter attribute.

        Single string are allowed in scatter filed in the CWL standard,
        so wrap them in an array.
        """
        if isinstance(scatter, str):
            scatter = [scatter]
        return scatter

    def model_post_init(self, __context):  # noqa ANN001
        """Extra validations and transformations."""
        # check scatter references only exisiting inputs.
        if self.scatter is not None:
            for input_name in self.scatter:
                if input_name not in self._inputs:
                    input_names = list(self._inputs)
                    err_msg = (
                        f"`{input_name}` declared in scatter configuration"
                        f" is not an input of step: `{self.id_}`."
                        f" Declared inputs are: `{input_names}`."
                    )
                    raise ScatterValidationError(err_msg)

            # check if we need a scatter method and set to default if required.
            if len(self.scatter) > 1 and not self.scatter_method:
                self.scatter_method = ScatterMethodEnum.dotproduct

    def __setattr__(
        self,
        name: str,
        value: Union[PythonValue, AssignableWorkflowStepOutput],
    ) -> None:
        """This is enabling assignment in our python DSL."""
        # model properties are accessed normally,
        # pydantic @computed_fields are automatically serialized
        # so let's use @property instead and check for those input names.
        if name in self.model_fields or name in ["_inputs", "_outputs"]:
            return super().__setattr__(name, value)

        # NOTE assignement are made on inputs only,
        # so check them first in case we have a input which is also an output.
        if self._inputs and name in self._inputs:
            input_ = self._inputs[name]
            input_.set_value(value)
        elif self._outputs and name in self._outputs:
            raise OutputAssignmentError(name)
        else:
            msg = f"undefined attribute {name}"
            raise AttributeError(msg)
        return None

    def __getattr__(
        self,
        name: str,
    ) -> Union[
        WorkflowStepInput,
        WorkflowStepOutput,
        tuple[WorkflowStepInput, WorkflowStepOutput],
    ]:
        """This is enabling assignment in our python DSL."""
        input_, output = None, None
        if self._outputs and name in self._outputs:
            output = self._outputs[name]

        if self._inputs and name in self._inputs:
            input_ = self._inputs[name]

        if input_ and output:
            logger.warning(
                f" step: {self.id_} has input and output of the same name: {name}"
                "returning (input, output)",
            )
            return (input_, output)

        if output:
            return output
        if input_:
            return input_

        raise AttributeError

    def serialize_value(
        self,
        input_: AssignableWorkflowStepInput,
    ) -> CWLValue:
        """Serialize input values."""
        return input_.type_.serialize_value(input_.value)

    def save_config(self, path: Path = Path()) -> Path:
        """Save the workflow configuration.

        Args:
            path: path to the directory in which to save the config.
            Default to the current working directory.

        Returns:
            Path to the config file.
        """
        config = {
            input_.id_: self.serialize_value(input_)
            for input_ in self.in_
            if input_.value is not None
        }

        path = directory_exists(path)

        file_path = path / (self.id_ + ".yaml")
        with Path.open(file_path, "w", encoding="utf-8") as file:
            file.write(yaml.dump(config))
            return file_path

    def input_ids(self) -> KeysView:
        """Return all step input ids."""
        return self._inputs.keys()

    def output_ids(self) -> KeysView:
        """Return all step output ids."""
        return self._outputs.keys()


# Placeholder for extra checks.
ProcessId = Annotated[str, []]


class Process(CwlRequireExtra, CwlDocExtra, CwlRootObject):
    """Process is the base class for all cwl models.

    It is the base classes for Workflows,CommandLineTools
    (and also Expression Tools and Operations)
    see (https://www.commonwl.org/user_guide/introduction/basic-concepts.html)
    """

    # NOTE important ignore unknown attributes.
    model_config = ConfigDict(extra="ignore")
    model_config = ConfigDict(populate_by_name=True)

    id_: ProcessId = Field(..., alias="id")
    cwl_version: str = Field("v1.2", alias="cwlVersion")
    class_: str = Field(..., alias="class")
    intent: Optional[list[str]] = Field(None)

    @property
    def _inputs(self) -> dict[ParameterId, InputParameter]:
        """Internal index to retrieve inputs efficiently."""
        return {input_.id_: input_ for input_ in self.inputs}

    @property
    def _outputs(self) -> dict[ParameterId, OutputParameter]:
        """Internal index to retrieve outputs efficiently."""
        return {output.id_: output for output in self.outputs}

    @property
    def name(self) -> str:
        """Generate a name from the id for convenience purpose."""
        return extract_name_from_id(self.id_)

    @field_validator("cwl_version", mode="before")
    @classmethod
    def validate_version(cls, version: str) -> str:
        """Check if the process version is v1.2."""
        # NOTE we log an warning instead
        msg = f"Process refers to older cwl version {version}. Loading anyway."
        logger.warning(msg)
        # if version and version != "v1.2":
        return version

    @classmethod
    def _load(cls, cwl_file: Union[Path, str]) -> dict:
        """Load a Process from a path or uri."""
        if isinstance(cwl_file, Path):
            cwl_file = file_exists(cwl_file)
        try:
            cwl_process = cwl_parser.load_document_by_uri(cwl_file)
        except CwlParserException:
            raise BadCwlProcessFileError(cwl_file) from Exception

        yaml_cwl = cwl_parser.save(cwl_process)

        if yaml_cwl["class"] == "Workflow" and yaml_cwl.get("steps"):
            # NOTE By default, save rewrite all ids and refs.
            # This would prevent us for recursively loading subprocesses so
            # for workflow we substitute with the original run references.
            full_refs_cwl = cwl_parser.save(cwl_process, relative_uris=False)
            runs = [step["run"] for step in full_refs_cwl["steps"]]
            for step, run in zip(yaml_cwl["steps"], runs):
                step["run"] = run

        return yaml_cwl

    @classmethod
    def load(
        cls,
        cwl_data: Union[Path, str, dict, "Process"],
        recursive: bool = False,
        context: Optional[dict] = None,
    ) -> "Process":
        """Load a process (optionally recursively).

        Factory method for all subclasses.
        The process can be referenced to by a path or uri,
        serialized as a dict or just be an existing model.

        Args:
            cwl_data: Path to the cwl file to load or an URI describing
        the resource location.
            recursive: If set to True, attempts to recursively load all
        cwl processes referenced.
            context: Collect all cwl models found.

        Returns:
            The process object.

        NOTE We use the reference cwl parser implementation to get a
        standardized description.
        """
        # create a context if we did not received one.
        if context is None:
            context = {}

        if isinstance(cwl_data, Process):
            process = cwl_data
        else:
            if isinstance(cwl_data, (Path, str)):
                cwl_data = cls._load(cwl_data)
            process_class = cwl_data["class"]
            if process_class == "Workflow":
                process = Workflow(**cwl_data)
            elif cwl_data["class"] == "CommandLineTool":
                process = CommandLineTool(**cwl_data)
            else:
                raise UnsupportedProcessClassError(process_class)

        if isinstance(process, Workflow) and recursive:
            for step in process.steps:
                Process.load(step.run, recursive=recursive, context=context)

        context[process.id_] = process
        return process

    def save(self, path: Optional[Path] = None) -> Path:
        """Create a cwl file.

        Process computed name is ignored.

        Args:
            path: Directory in which in to create the file.
        """
        if path is None:
            path = Path()

        path = directory_exists(path)
        file_path = path / (self.name + ".cwl")
        serialized_process = self.model_dump(
            by_alias=True,
            exclude={"name"},
            exclude_none=True,
        )
        with Path.open(file_path, "w", encoding="utf-8") as file:
            file.write(yaml.dump(serialized_process))
            return file_path


class Workflow(Process):
    """Represents a CWL Workflow.

    Workflows are represented by inputs outputs and a list of steps.
    """

    model_config = ConfigDict(populate_by_name=True)

    inputs: list[WorkflowInputParameter]
    outputs: list[WorkflowOutputParameter]
    steps: list[WorkflowStep]

    from_builder: Optional[bool] = Field(False, exclude=True)
    class_: str = Field(alias="class", default="Workflow")

    @field_validator("class_", mode="before")
    @classmethod
    def validate_class(cls, class_: str) -> str:
        """Check we are parsing a workflow."""
        if class_ and class_ != "Workflow":
            msg = "Workflow"
            raise UnexpectedClassError(msg, class_)
        return class_

    def save_config(self, path: Path = Path()) -> Path:
        """Generate config file for the configured workflow."""
        wf: Workflow = polus.tools.workflows.builders.StepBuilder()(self)
        return wf.save_config(path)


class CommandLineTool(Process):
    """Represent a CommandLineTool."""

    model_config = ConfigDict(populate_by_name=True)

    inputs: list[CommandInputParameter]
    outputs: list[CommandOutputParameter]
    class_: str = Field(alias="class", default="CommandLineTool")

    base_command: Optional[str] = Field(None, alias="baseCommand")
    stdin: Optional[str] = None
    stderr: Optional[str] = None
    stdout: Optional[str] = None
    arguments: Optional[list[Union[str, Expression, CommandLineBinding]]] = Field(None)
    success_codes: Optional[list[int]] = Field(None, alias="successCodes")
    temporary_fail_codes: Optional[list[int]] = Field(None, alias="temporaryFailCodes")
    permanent_fail_codes: Optional[list[int]] = Field(None, alias="permanentFailCodes")

    @field_validator("class_", mode="before")
    @classmethod
    def validate_class(cls, class_: str) -> str:
        """Check we are parsing a command line tool."""
        if class_ and class_ != "CommandLineTool":
            msg = "CommandLineTool"
            raise UnexpectedClassError(msg, class_)
        return class_


class ExpressionTool(Process):
    """Expression Tool are wrapping javascript code."""

    pass


class Operation(Process):
    """Operation are used for no-op placeholder."""

    pass
