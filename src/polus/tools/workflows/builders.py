"""Builders."""

from pathlib import Path
from typing import Optional
from typing import TypedDict
from typing import Union

from pydantic import ValidationError
from typing_extensions import NotRequired
from typing_extensions import Unpack

from polus.tools.workflows.default_ids import generate_cwl_source_repr
from polus.tools.workflows.default_ids import generate_default_input_path
from polus.tools.workflows.default_ids import generate_default_step_id
from polus.tools.workflows.default_ids import generate_step_id
from polus.tools.workflows.default_ids import generate_workflow_io_id
from polus.tools.workflows.default_ids import generate_worklfow_id
from polus.tools.workflows.exceptions import CannotParseAdditionalInputParamError
from polus.tools.workflows.exceptions import UnsupportedCaseError
from polus.tools.workflows.exceptions import WhenClauseValidationError
from polus.tools.workflows.model import AssignableWorkflowStepInput
from polus.tools.workflows.model import AssignableWorkflowStepOutput
from polus.tools.workflows.model import Process
from polus.tools.workflows.model import Workflow
from polus.tools.workflows.model import WorkflowInputParameter
from polus.tools.workflows.model import WorkflowOutputParameter
from polus.tools.workflows.model import WorkflowStep
from polus.tools.workflows.model import WorkflowStepInput
from polus.tools.workflows.requirements import InlineJavascriptRequirement
from polus.tools.workflows.requirements import ProcessRequirement
from polus.tools.workflows.requirements import ScatterFeatureRequirement
from polus.tools.workflows.requirements import SubworkflowFeatureRequirement
from polus.tools.workflows.types import CWLArray
from polus.tools.workflows.types import CWLBasicType
from polus.tools.workflows.types import CWLBasicTypeEnum
from polus.tools.workflows.types import CWLType


class StepBuilder:
    """Create a workflow step.

    Create a WorkflowStep from a Process.
    For each input/output of the clt, a corresponding step in/out is created.
    """

    def __init__(  # noqa: PLR0913 - we want to provide hints to user.
        self,
        process: Process,
        scatter: Optional[list[str]] = None,
        when: Optional[str] = None,
        add_inputs: Optional[list[dict]] = None,
        when_input_names: Optional[list[str]] = None,
    ) -> None:
        """Set up Step factory."""
        # TODO we could make this a default strategy that
        # can be overriden by the user.
        step_id = generate_default_step_id(process.name)
        run = process.id_

        inputs = [
            AssignableWorkflowStepInput(
                id=input_.id_,
                source=None,
                type=self._promote_cwl_type(input_.type_)
                if scatter and input_.id_ in scatter
                else input_.type_,
                optional=input_.optional,
                step_id=step_id,
            )
            for input_ in process.inputs
        ]

        # TODO Check spec. If scatter is present all outputs
        # should be scattered.
        outputs = [
            AssignableWorkflowStepOutput(
                id=output.id_,
                type=self._promote_cwl_type(output.type_) if scatter else output.type_,
                step_id=step_id,
            )
            for output in process.outputs
        ]

        parsed_add_inputs = self.process_additional_inputs(add_inputs)

        self.process_when_clause(process, parsed_add_inputs, when, when_input_names)

        # Generate additional inputs.
        # For example,if the conditional clause contains unknown inputs.
        # It could also be to generate fake inputs for wic compatibility.
        if parsed_add_inputs:
            inputs = inputs + [
                AssignableWorkflowStepInput(
                    id=input_.id_,
                    source=None,
                    type=self._promote_cwl_type(
                        input_.type_,
                    )
                    if scatter and input_.id_ in scatter
                    else input_.type_,
                    optional=input_.optional,
                    step_id=step_id,
                )
                for input_ in parsed_add_inputs
            ]

        self.step = WorkflowStep(
            scatter=scatter,
            when=when,
            id=step_id,
            run=run,
            in_=inputs,
            out=outputs,
            from_builder=True,
        )

        # For a workflow, bubble up values assigned to its steps.
        # Those become values of the workflow inputs.
        if isinstance(process, Workflow):
            for step in process.steps:
                for input_ in step.in_:
                    if (
                        isinstance(input_, AssignableWorkflowStepInput)
                        and input_.source in self.step._inputs
                    ):
                        self.step._inputs[input_.source].value = input_.value
                        self.step._inputs[input_.source]

    def _promote_cwl_type(self, type_: CWLType) -> CWLArray:
        """Promoting types.

        When scattering over some inputs,
        we need to provide arrays of value of the original types.
        """
        return CWLArray(items=type_)

    def process_additional_inputs(
        self,
        add_inputs: Optional[list[dict]],
    ) -> Optional[list[WorkflowInputParameter]]:
        """Process additional inputs.

        Parse into workflow step input to detect basic problems early.
        """
        parsed_add_inputs: Optional[list[WorkflowInputParameter]] = None
        if add_inputs:
            try:
                parsed_add_inputs = [
                    WorkflowInputParameter(**input_) for input_ in add_inputs
                ]
            except ValidationError:
                msg = "additional input description is invalid!"
                raise CannotParseAdditionalInputParamError(
                    msg,
                ) from ValidationError
        return parsed_add_inputs

    def process_when_clause(
        self,
        process: Process,
        add_inputs: Optional[list[WorkflowInputParameter]],
        when: Optional[str],
        when_input_names: Optional[list[str]],
    ) -> None:
        """Process when clause.

        Inputs referenced in the when clause may or may not be already declared
        if the process. If not, user must provide a description of it.
        """
        # TODO we could evaluate the clause rather than having the user declare
        # explicitly.
        if when:
            if not when_input_names:
                msg = "You need to specify which inputs\
                    are referenced in the when clause."
                raise WhenClauseValidationError(msg)

            _add_inputs_ids = (
                {input_.id_ for input_ in add_inputs} if add_inputs else set()
            )
            _process_inputs_ids = {input_.id_ for input_ in process.inputs}
            for when_input_name in when_input_names:
                if (
                    when_input_name not in _process_inputs_ids
                    and when_input_name not in _add_inputs_ids
                ):
                    msg = "Input in when clause unknown.\
                            Please add its declaration to add_inputs arguments."
                    raise WhenClauseValidationError(msg)

    def __call__(self) -> WorkflowStep:
        """Returns the fully constructed WorkflowStep."""
        return self.step


class WorkflowBuilder:
    """Builder for a workflow object.

    Enable creating workflow dynamically.
    """

    class Options(TypedDict):
        """WorkflowBuilder options."""

        workdir: NotRequired[Path]
        recursive: NotRequired[bool]
        context: NotRequired[dict]
        steps: NotRequired[list[WorkflowStep]]

    # TODO probably split between factory option
    # and workflow generation.
    def __init__(  # noqa: C901
        self,
        id_: str,
        **kwds: Unpack[Options],
    ) -> None:
        """Set up the workflow factory options."""
        context = {}
        recursive = True

        steps = kwds.get("steps", [])
        self.workdir = kwds.get("workdir", Path())
        recursive = kwds.get("recursive", True)
        context = kwds.get("context", {})
        add_step_index = True

        if not steps:
            steps = []

        # Collect all step inputs and create a workflow input for each
        # Collect all step outputs and create a workflow output for each
        # NOTE For now each output from each step creates an output.
        # TODO Make this optional.
        # TODO We could also reduced workflow outputs to only those
        # which are not already connected.
        # TODO Similarly we could have an option to hide/rename
        # workflow inputs.
        # TODO Many possible strategies here:
        # We could change that, make that a user provided option,
        # generate simpler names if no clash are detected
        # or provide ability for aliases...
        workflow_inputs = []
        workflow_outputs = []
        scatter_requirement = False
        subworkflow_feature_requirement = False
        inline_javascript_requirement = False

        if add_step_index:
            self.update_steps_references_with_index(steps)

        for step in steps:
            # if we have the definition already in context, just use it.
            # Subprocesses will not be loaded either.
            if step.run not in context:
                Process.load(step.run, recursive=recursive, context=context)

            # TODO CHECK if we would to look recursively or not
            # update workflow requirements
            if step.scatter:
                scatter_requirement = True
            if step.when:
                inline_javascript_requirement = True

            for input_ in step.in_:
                # Only create workflows inputs and connect to them
                # if step inputs are not already connected to another step output.
                if input_.source is not None:
                    continue
                # Ignore unset optional inputs
                # NOTE needed because the cwl standard does not allow for unset values.
                if input_.optional and input_.value is None:
                    continue

                self.generate_default_workflow_inputs(
                    input_,
                    step,
                    steps,
                )

                workflow_input_id = generate_workflow_io_id(
                    id_,
                    step.id_,
                    input_.id_,
                )
                workflow_input = WorkflowInputParameter(
                    id=workflow_input_id,
                    type=input_.type_,
                )
                input_.source = workflow_input_id
                workflow_inputs.append(workflow_input)

            for output in step.out:
                workflow_output_id = generate_workflow_io_id(
                    id_,
                    step.id_,
                    output.id_,
                )

                workflow_output = WorkflowOutputParameter(
                    id=workflow_output_id,
                    type=output.type_,
                    output_source=generate_cwl_source_repr(step.id_, output.id_),
                )
                workflow_outputs.append(workflow_output)

        # Detect if we need to add subworkflowFeatureRequirement.
        for process in context.values():
            if process.class_ == "Workflow":
                subworkflow_feature_requirement = True
                break

        requirements = self.set_requirements(
            scatter_requirement,
            subworkflow_feature_requirement,
            inline_javascript_requirement,
        )

        id_ = generate_worklfow_id(self.workdir, id_)

        self.workflow = Workflow(
            id=id_,
            steps=steps,
            inputs=workflow_inputs,
            outputs=workflow_outputs,
            requirements=requirements,
            from_builder=True,
        )

    def __call__(self) -> Workflow:
        """Save the workflow description and return the workflow object."""
        # TODO figure out if we want to first set the factory, then
        # initialize the workflow or keep things as they are.
        # NOTE this could be revisited, but
        # we need to be able to load the original cwl when creating workflows
        # that use this workflow.
        self.workflow.save(self.workdir)
        return self.workflow

    def generate_default_workflow_inputs(
        self,
        input_: WorkflowStepInput,
        step: WorkflowStep,
        steps: list[WorkflowStep],
    ) -> Union[Path, None]:
        """Generate default workflow inputs if needed.

        if a step input is also a step output,
        and this step output is linked to other step inputs,
        then we need to generate a default value for this input
        and bubble it up as a workflow input value.
        This allows further manual customization.
        """
        # TODO we could also expose that the user and have him customized
        # the generated name.
        if input_.id_ not in step._outputs:
            return None
        # if input is output, build its source representation
        _ref = generate_cwl_source_repr(step.id_, input_.id_)
        # check if another step input reference this output
        for _other_step in steps:
            if _other_step == step:
                continue
            for _input in _other_step.in_:
                if _input.source == _ref:
                    # NOTE Review later. It may be allowable to link
                    # (nested) array of dirs.
                    # But then we cannot anticipate the number of
                    # directories to create
                    # before runtime.
                    if not (
                        _input.type_ != CWLBasicType(type=CWLBasicTypeEnum.DIRECTORY)
                        or _input.type_ != CWLBasicType(type=CWLBasicTypeEnum.FILE)
                    ):
                        msg = f"Error while building workflow.\
                            Error generating while default workflow inputs.\
                            Unexpected type: {_input.type_}."
                        raise UnsupportedCaseError(
                            msg,
                        )
                    input_.value = generate_default_input_path(step.id_, input_.id_)
                    return input_.value
        return None

    def set_requirements(
        self,
        scatter_requirement: bool,
        subworkflow_feature_requirement: bool,
        inline_javascript_requirement: bool,
    ) -> list[ProcessRequirement]:
        """Return a list of Process Requirements."""
        requirements = []
        if scatter_requirement:
            # TODO CHECK cwl spec. if multiple inputs,
            # we also need to add a scatter method.
            requirements.append(ScatterFeatureRequirement())
        if subworkflow_feature_requirement:
            requirements.append(SubworkflowFeatureRequirement())
        if inline_javascript_requirement:
            requirements.append(InlineJavascriptRequirement())
        return requirements

    def update_steps_references_with_index(
        self,
        steps: list[WorkflowStep],
    ) -> list[WorkflowStep]:
        """Update steps references with a unique index.

        Whenever certain steps are used more than once in the same workflow,
        the step references will become ambiguous.
        Preprocess step ids to prepend a unique index and update all references.
        """
        updated_step_ids: dict[str, str] = {
            step.id_: generate_step_id(step.id_, prefix=str(index))
            for (index, step) in enumerate(steps)
        }
        for step in steps:
            step.id_ = updated_step_ids[step.id_]
            for input_ in step.in_:
                if input_.source is not None:
                    (source_step_id, param_id) = input_.source.split("/")
                    input_.source = generate_cwl_source_repr(
                        updated_step_ids[source_step_id],
                        param_id,
                    )

        return steps
