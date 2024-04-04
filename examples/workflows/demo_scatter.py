"""Example of building and running a workflow with scattered inputs."""

from pathlib import Path

from polus.tools.workflows.backends import run_cwl
from polus.tools.workflows.builders import StepBuilder
from polus.tools.workflows.builders import WorkflowBuilder
from polus.tools.workflows.logger import get_logger
from polus.tools.workflows.model import CommandLineTool
from polus.tools.workflows.model import ScatterMethodEnum
from polus.tools.workflows.utils import configure_folders

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)

logger = get_logger(__name__)

test_data_dir = Path("tests") / "workflows" / "test_data"
clt_files = [
    test_data_dir / "echo_string.cwl",
    test_data_dir / "uppercase2_wic_compatible2_optional.cwl",
]

(echo, uppercase) = (CommandLineTool.load(cwl_file) for cwl_file in clt_files)

# scatter all inputs for echo
scattered_inputs = [input_.id_ for input_ in echo.inputs]
step1 = StepBuilder()(echo, scatter=scattered_inputs)

# scatter all inputs for uppercase
scattered_inputs = [input_.id_ for input_ in uppercase.inputs]
step2 = StepBuilder()(
    uppercase,
    scatter=scattered_inputs,
    # NOTE if not set default to dot_product
    scatter_method=ScatterMethodEnum.flat_crossproduct,
)

# linking scattered steps
step2.message = step1.message_string
step2.uppercase_message = step1.message_string

# set some values for the first step.
step1.message = ["hello", "world"]

# build the workflow
wf_builder = WorkflowBuilder(workdir=OUTPUT_DIR)
wf = wf_builder("wf_scatter", steps=[step1, step2])

# save files
wf_file = wf.save(OUTPUT_DIR)
config_file = StepBuilder()(wf).save_config(OUTPUT_DIR)

# execute locally
run_cwl(wf_file, config_file=config_file, cwd=STAGING_DIR)
