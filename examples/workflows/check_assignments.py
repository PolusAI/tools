"""Example of building and running a workflow with scattered inputs."""

from pathlib import Path

from polus.tools.workflows.backends import run_cwl
from polus.tools.workflows.builders import StepBuilder
from polus.tools.workflows.builders import WorkflowBuilder
from polus.tools.workflows.exceptions import OutputAssignmentError
from polus.tools.workflows.logger import get_logger
from polus.tools.workflows.model import CommandLineTool
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

step1 = StepBuilder()(echo)
step2 = StepBuilder()(uppercase)

# linking steps
step2.message = step1.message_string
# set some values for the first step.
step1.message = "hello"

# show what happened with some bad assignments.
try:
    step2.non_existing_input = step1.message_string
except AttributeError as e:
    logger.warn(e)

try:
    step2.uppercase_message = step1.non_existing_output
except AttributeError as e:
    logger.warn(e)

try:
    step1.message_string = step2.uppercase_message
except OutputAssignmentError as e:
    logger.warn(e)

# build the workflow
wf_builder = WorkflowBuilder(workdir=OUTPUT_DIR)
wf = wf_builder("chek_assignment", steps=[step1, step2])

# save files
wf_file = wf.save(OUTPUT_DIR)
config_file = StepBuilder()(wf).save_config(OUTPUT_DIR)

# execute locally
run_cwl(wf_file, config_file=config_file, cwd=STAGING_DIR)
