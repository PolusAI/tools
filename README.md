# Polus Tools

## polus.tool.workflows

This package provides model that represents CWL workflows and command line
tools following the latest [cwl spec](https://www.commonwl.org/v1.2/).
It also provides tools to load, save, build and execute cwl tools and workflows.
It requires no configuration and focus on ease of use and modularity.

### How to install

Use you prefered method to create a new environment then :

with pip: `pip install .`
or with poetry:  `poetry install`

### How to use

`python examples/workflows/demo_image_processing.py` for a basic example of use.

This tool allows people to load clts and workflows from a path or a URI.
The `CommandLineTool` and `Workflow` models are found in `polus.tools.workflow.model`.
Then workflows can be build thanks to two builder classes : `StepBuilder` and `WorkflowBuilder`.
Those builders are configurable to further customize how they operate.

The tool provide an easy way to configure a workflow through regular python assignments.
Ex:
assigning a value to a step input :  `step1.inputA = "input_message"`
linking an step output to another step input : `step2.inputA = step1.outputA`

Once configured and build, a `workflow` object can be persisted with `workflow.save()`
and its configuration with `workflow.save_config()`

Lastly we provide a convenience method to run workflows locally with `cwltool`
by calling `polus.tools.workflows.backends.run_cwl()`.

### Structure

`src/polus/tools/workflows` contains the source code.
`tests/workflows` contains the test suite.
`tests/worklflows/test_data` contains a variety of cwl processes definitions.
`examples` contains our examples.

Other data directories:
`cwl` contains cwl definitions of processes we use as building blocks.
`cwl_generated` contains cwl definitions of processes generated by the tool.
`tmp` will be created on the first run and will contains examples outputs.


### Current Workflow features

This tool supports creating workflows containing:
- subworkflows
- conditional clauses
- scattered inputs
- multiple inputs


### Developers

Some hooks should run on commits. Please run `pre-commit install` to set up the hooks
before contributing.
