"""Example of building and running a workflow with scattered inputs."""

from pathlib import Path

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
clt_files = ["echo_string.cwl", "uppercase2_wic_compatible3.cwl"]

clts = []
for filename in clt_files:
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    clts.append(clt)

(echo, uppercase) = clts

# scatter all inputs for echo
scattered_inputs = [input_.id_ for input_ in echo.inputs]
step1 = StepBuilder()(echo, scatter=scattered_inputs)

# scatter all inputs for uppercase
scattered_inputs = [input_.id_ for input_ in uppercase.inputs]
step2 = StepBuilder()(uppercase, scatter=scattered_inputs)

# linking scattered steps
step2.message = step1.message_string

try:
    step2.uppercase_message = step1.message_string
except OutputAssignmentError as e:
    logger.warn(e)


wf_builder = WorkflowBuilder(workdir=OUTPUT_DIR)
wf = wf_builder("wf_scatter", steps=[step1, step2])

# TODO RUN
