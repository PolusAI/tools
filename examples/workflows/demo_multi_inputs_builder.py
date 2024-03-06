"""Test building and  configuring multi-inputs.

Build a workflow with multiple outputs feeding to one input.
"""

from pathlib import Path

from polus.tools.workflows import CommandLineTool
from polus.tools.workflows.backends import run_cwl
from polus.tools.workflows.builders import StepBuilder
from polus.tools.workflows.builders import WorkflowBuilder
from polus.tools.workflows.logger import get_logger
from polus.tools.workflows.utils import configure_folders

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)

logger = get_logger(__name__)

test_data_dir = Path("tests") / "workflows" / "test_data"
filename = "multi-inputs-workflow.cwl"

clt_files = [
    test_data_dir / "echo_string.cwl",
    test_data_dir / "uppercase2_wic_compatible3.cwl",
]

(echo, uppercase) = (CommandLineTool.load(cwl_file) for cwl_file in clt_files)

echo1 = StepBuilder()(echo, id_="echo1")
echo2 = StepBuilder()(echo, id_="echo2")
# we scatter over the touch input to enable the multi-inputs connection.
uppercase_scatter = StepBuilder()(uppercase, scatter="message")
# we provide 2 outputs to the same input
uppercase_scatter.message = [echo1.message_string, echo2.message_string]

wf = WorkflowBuilder()("multi_inputs", steps=[echo1, echo2, uppercase_scatter])

# we always configure a step
wf_step = StepBuilder()(wf)

# check input names
print("input names: ", *wf_step.input_ids(), sep="\n")  # noqa: T201

# configure
wf_step.multi_inputs___0__echo1___message = "hello"
wf_step.multi_inputs___1__echo2___message = "world"

# save files
wf_file = wf.save(OUTPUT_DIR)
config_file = wf_step.save_config(OUTPUT_DIR)

# execute locally
run_cwl(wf_file, config_file=config_file, cwd=STAGING_DIR)
