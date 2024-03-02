"""Model."""

from pathlib import Path
from typing import Annotated
from typing import Any
from typing import Optional
from typing import Union
from urllib.parse import unquote
from urllib.parse import urlparse

import cwl_utils.parser as cwl_parser
import yaml  # type: ignore[import]
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import SerializerFunctionWrapHandler
from pydantic import WrapSerializer
from pydantic import field_serializer
from pydantic.functional_validators import AfterValidator
from pydantic.functional_validators import field_validator
from rich import print
from schema_salad.exceptions import ValidationException as CwlParserException

from polus.tools.workflows.default_ids import generate_cwl_source_repr
from polus.tools.workflows.exceptions import BadCwlProcessFileError
from polus.tools.workflows.exceptions import IncompatibleTypeError
from polus.tools.workflows.exceptions import IncompatibleValueError
from polus.tools.workflows.exceptions import NotAFileError
from polus.tools.workflows.exceptions import UnexpectedTypeError
from polus.tools.workflows.exceptions import UnsupportedProcessClassError
from polus.tools.workflows.requirements import ProcessRequirement
from polus.tools.workflows.types import CWLType
from polus.tools.workflows.types import PythonValue
from polus.tools.workflows.utils import directory_exists
from polus.tools.workflows.utils import file_exists


class InputBinding(BaseModel):
    """Base class for any Input Binding."""

    pass


class CommandLineInputBinding(InputBinding):
    """CommandLineInputBinding.

    Describe how to translate the input parameter to a
    program argument.
    Cwl parser's counterpart is CommandLineBinding.
    """

    # TODO Capture other missing attributes.
    position: Optional[int] = None


class CommandLineOutputBinding(BaseModel):
    """CommandLineOutputBinding.

    Describe how to translate the wrapped program result
    into a an output parameter.

    cwl parser's counterpart is CommandOutputBinding.
    """

    model_config = ConfigDict(populate_by_name=True)

    glob: Optional[str] = None
    load_contents: Optional[bool] = Field(None, alias="loadContents")
    output_eval: Optional[str] = Field(None, alias="outputEval")


# TODO checks for parameter ids?
def is_valid_parameter_id(id_: str) -> str:
    """Check if parameter id is valid."""
    return id_


ParameterId = Annotated[str, [is_valid_parameter_id]]


class Parameter(BaseModel):
    """Parameter.

    Base representation of any parameters.
    Every parameter must have an id and a type.
    We also track if the parameter is optional or not
    (CWL encodes this information in the type declaration).
    """

    model_config = ConfigDict(populate_by_name=True)

    id_: ParameterId = Field(..., alias="id")
    # TODO make optional a parameter so it cannot be set
    # but only derived from type.
    # Check if we will still be able to retrieve it in the
    # type field validator.
    optional: bool = Field(False, exclude=True)
    type_: CWLType = Field(..., alias="type")

    @field_validator("type_", mode="before")
    @classmethod
    # TODO CHECK type of optional
    def transform_type(cls, type_: CWLType, optional: Any = None) -> CWLType:  # noqa
        """Check if we have an optional type."""
        if isinstance(type_, list):
            # CHECK for optional types
            if type_[0] == "null":
                # TODO check alternatives.
                # feels a bit hacky to modify the model this way.
                optional.data["optional"] = True
                return cls.transform_type(type_[1])
            raise UnexpectedTypeError(type_)
        return type_


class InputParameter(Parameter):
    """Base class of any input parameter."""

    pass


class OutputParameter(Parameter):
    """Base class of any input parameter."""

    pass


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

    # TODO CHECK maybe add additional constraints?
    output_source: str = Field(..., alias="outputSource")


class CommandInputParameter(InputParameter):
    """Command Line Tool input parameter."""

    model_config = ConfigDict(populate_by_name=True)

    input_binding: Optional[CommandLineInputBinding] = Field(None, alias="inputBinding")


class CommandOutputParameter(OutputParameter):
    """Command Line Tool output parameter."""

    model_config = ConfigDict(populate_by_name=True)

    output_binding: Optional[CommandLineOutputBinding] = Field(
        None,
        alias="outputBinding",
    )


# TODO CHECK if we need extra validation.
def is_valid_stepio_id(id_: str) -> str:
    """Check if we have a valid step input/output io id."""
    return id_


StepIOId = Annotated[str, [is_valid_stepio_id]]


class WorkflowStepOutput(BaseModel):
    """WorkflowStepOuput.

    WorkflowStepOuput define the name of a step output that can be used
    as a reference for in another step input or a workflow output.
    """

    model_config = ConfigDict(populate_by_name=True)
    id_: StepIOId = Field(..., alias="id")


class AssignableWorkflowStepOutput(WorkflowStepOutput):
    """AssignableWorkflowStepOutput.

    This a special kind of WorkflowStepOutput that can
    be dynamically link to another step input.
    """

    model_config = ConfigDict(populate_by_name=True)

    type_: CWLType = Field(exclude=True, alias="type")
    value: Any = None
    step_id: str


class WorkflowStepInput(BaseModel):
    """WorkflowStepInput.

    It describes how to provide an input to a workflow step.
    It provides a ref to a workflow input or another step output.
    """

    model_config = ConfigDict(populate_by_name=True)

    id_: StepIOId = Field(..., alias="id")
    source: Optional[str]


class AssignableWorkflowStepInput(WorkflowStepInput):
    """AssignableWorkflowStepInput.

    This a special kind of WorkflowStepInput that can
    have values assigned to or can be linked to another
    workflow input or step output.
    """

    model_config = ConfigDict(populate_by_name=True)

    type_: CWLType = Field(exclude=True, alias="type")
    value: PythonValue = None
    optional: bool = Field(exclude=True)
    step_id: str

    def set_value(
        self,
        value: Union[PythonValue, AssignableWorkflowStepOutput],
    ) -> None:
        """Assign a value to this step input or link it to another step output."""
        if isinstance(value, AssignableWorkflowStepOutput):
            if self.type_ != value.type_:
                raise IncompatibleTypeError(self.type_, value.type_)
            self.source = generate_cwl_source_repr(value.step_id, value.id_)
        elif value is not None:
            if not self.type_.is_value_assignable(value):
                raise IncompatibleValueError(self.id_, self.type_, value)
        else:
            # TODO remove when poc is completed.
            msg = "this case is not properly handled."
            raise NotImplementedError(msg)
        self.value = value


WorkflowStepId = Annotated[str, []]


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


class WorkflowStep(BaseModel):
    """Capture a workflow step.

    A workflow step has an id so it can be referenced by other steps,
    or workflow ios.
    It has a list of inputs whose ids correspond to the process input ids they
    are wrapping and describe to which workflow input/step outputs they connect.
    It has a list of outputs whose ids correspond to the process output ids they
    are wrapping and describe to  which workflow inputs they connect.
    """

    # needed because of the reserved keyword are used in the model.
    model_config = ConfigDict(populate_by_name=True)

    id_: WorkflowStepId = Field(..., alias="id")
    run: Union[str, "Process"]
    in_: WorkflowStepInputs = Field(..., alias="in")
    out: WorkflowStepOutputs = Field(...)

    @property
    def _inputs(self) -> dict[StepIOId, WorkflowStepInput]:
        """Generate a dict of WorkflowStepInputs for efficient retrieval."""
        return {input_.id_: input_ for input_ in self.in_}

    @property
    def _outputs(self) -> dict[StepIOId, WorkflowStepOutput]:
        """Generate a dict of WorkflowStepOutputs for efficient retrieval."""
        return {output.id_: output for output in self.out}

    # TODO CHECK that ids exists?
    scatter: Optional[list[str]] = Field(None)  # ref to scatter inputs

    # TODO CHECK that.
    when: Optional[str] = Field(None)  # ref to conditional execution clauses

    # TODO CHECK we may remove that later
    from_builder: Optional[bool] = Field(False, exclude=True)

    @field_serializer("out", when_used="always")
    @classmethod
    def serialize_type(cls, out: WorkflowStepOutputs) -> list[str]:
        """When serializing, return only the list of ids."""
        return [output.id_ for output in out]

    @field_validator("out", mode="before")
    @classmethod
    def preprocess_workflow_step_output(
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

    def __setattr__(
        self,
        name: str,
        value: Union[PythonValue, AssignableWorkflowStepOutput],
    ) -> None:
        """This is enabling assignment in our python DSL."""
        if name in ["in_", "_inputs", "out", "_outputs", "id_", "run"]:
            return super().__setattr__(name, value)
        if self._inputs and name in self._inputs:
            input_ = self._inputs[name]
            input_.set_value(value)
            print(input_)
            return None
        if self._outputs and name in self._outputs:
            output = self._outputs[name]
            output.set_value(value)
            return None
        msg = f"undefined attribute {name}"
        raise AttributeError(msg)

    def __getattr__(self, name: str) -> Union[WorkflowStepInput, WorkflowStepOutput]:
        """This is enabling assignment in our python DSL."""
        # TODO CHECK Note there is an ordering issues here
        # if we ever need to check inputs because
        # a input and an output can have the same name!
        # NOTE we could disambiguate in from out if necessary
        # NOTE similarly, we could create unique step name if necessary.
        # (in case the same step is repeated n times).
        if self._outputs and name in self._outputs:
            return self._outputs[name]

        # TODO CHECK return defensive copy / read-only?
        # we can use inputs to check property of the workflow
        if self._inputs and name in self._inputs:
            return self._inputs[name]

        raise AttributeError

    def serialize_value(
        self,
        input_: AssignableWorkflowStepInput,
    ) -> Union[dict, list, PythonValue]:
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
            # TODO CHECK how configurable this process is.
            # ex: we generate list but we could also generate dictionaries.
            file.write(yaml.dump(config))
            return file_path


# TODO CHECK Unused
def process_exists_locally(id_: str) -> str:
    """Check the process id (which is an uri) points to an existing file on disk."""
    # TODO check if we need that.
    # NOTE when building new workflow, the file is not yet present on disk.
    # NOTE we may have remote definitions. What to do then?
    try:
        path = Path(unquote(urlparse(id_).path))
        path = file_exists(path)
    except (ValueError, FileNotFoundError, NotAFileError) as e:
        raise BadCwlProcessFileError(id_) from e
    if path.suffix != ".cwl":
        raise BadCwlProcessFileError(id_)
    return id_


def is_processid_uri(id_: str) -> str:
    """Check we have a valid uri."""
    # TODO throw custom exception?
    Path(unquote(urlparse(id_).path))
    return id_


"""
ProcessId needs to points to an existing file on disk
in order to be pulled in a Workflow definition.
However, when we first instantiated a newly buildworkfow, the
files does not yet exists on disk.
"""
ProcessId = Annotated[str, AfterValidator(is_processid_uri)]


class Process(BaseModel):
    """Process is the base class for all cwl models.

    It is the base classes for Workflows,CommandLineTools
    (and also Expression Tools and Operations)
    see (https://www.commonwl.org/user_guide/introduction/basic-concepts.html)
    """

    model_config = ConfigDict(populate_by_name=True)

    id_: ProcessId = Field(..., alias="id")
    cwl_version: str = Field("v1.2", alias="cwlVersion")
    class_: str = Field(..., alias="class")
    doc: Optional[str] = None
    label: Optional[str] = None
    requirements: Optional[list[ProcessRequirement]] = None

    # TODO CHECK if necessary
    @property
    def _inputs(self) -> dict[ParameterId, InputParameter]:
        """Internal index to retrieve inputs efficiently."""
        return {input_.id_: input_ for input_ in self.inputs}

    # TODO CHECK if necessary
    @property
    def _outputs(self) -> dict[ParameterId, OutputParameter]:
        """Internal index to retrieve outputs efficiently."""
        return {output.id_: output for output in self.outputs}

    @property
    def name(self) -> str:
        """Generate a name from the id for convenience purpose."""
        # TODO CHECK this works for any allowable CLT
        return Path(self.id_).stem

    @field_validator("cwl_version", mode="before")
    @classmethod
    def validate_version(cls, version: str) -> str:
        """Check if the process version is v1.2."""
        if version and version != "v1.2":
            msg = f"Unsupported version: {version}. Only v1.2 is supported."
            raise Exception(msg)
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
            # by default, save rewrite all ids and refs.
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
            msg = "bad class"
            raise Exception(msg, class_)
        return class_


class CommandLineTool(Process):
    """Represent a CommandLineTool."""

    # TODO Check we are adopting the correct strategy
    model_config = ConfigDict(extra="ignore")
    model_config = ConfigDict(populate_by_name=True)

    inputs: list[CommandInputParameter]
    outputs: list[CommandOutputParameter]
    # TODO Check after running hooks
    base_command: Optional[str] = Field(None, alias="baseCommand")
    stdout: Optional[str] = None
    class_: str = Field(alias="class", default="CommandLineTool")

    @field_validator("class_", mode="before")
    @classmethod
    def validate_class(cls, class_: str) -> str:
        """Check we are parsing a command line tool."""
        if class_ and class_ != "CommandLineTool":
            msg = "bad class"
            raise Exception(msg, class_)
        return class_


class ExpressionTool(Process):
    """Expression Tool are wrapping javascript code."""

    pass


class Operation(Process):
    """Operation are used for no-op placeholder."""

    pass
