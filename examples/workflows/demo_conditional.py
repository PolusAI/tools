"""Example of building and running a workflow with conditional clauses."""

from pathlib import Path

from polus.tools.workflows.backends import run_cwl
from polus.tools.workflows.builders import StepBuilder
from polus.tools.workflows.builders import WorkflowBuilder
from polus.tools.workflows.logger import get_logger
from polus.tools.workflows.model import Process
from polus.tools.workflows.utils import configure_folders

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)

logger = get_logger(__name__)

clt_files = ["workflow3.cwl", "touch_single.cwl"]
test_data_dir = Path("tests") / "workflows" / "test_data"
clt_paths = [test_data_dir / clt_file for clt_file in clt_files]


(echo_uppercase_wf_clt, touch_clt) = (Process.load(cwl_path) for cwl_path in clt_paths)


echo_uppercase_wf = StepBuilder()(echo_uppercase_wf_clt)
# create a step with a conditional clause
touch = StepBuilder()(
    touch_clt,
    when="$(inputs.should_execute < 1)",
    when_input_names=["should_execute"],
    add_inputs=[{"id": "should_execute", "type": "int"}],
)

# linking steps
touch.touchfiles = echo_uppercase_wf.uppercase_message

# set input values
echo_uppercase_wf.in_[0].value = "hello"
touch.in_[1].value = 1

# building workflow
wf = WorkflowBuilder(workdir=OUTPUT_DIR)(
    "workflow_conditional",
    steps=[echo_uppercase_wf, touch],
)

# save files
wf_file = wf.save(OUTPUT_DIR)
config_file = StepBuilder()(wf).save_config(OUTPUT_DIR)

# execute locally
run_cwl(wf_file, config_file=config_file, cwd=STAGING_DIR)
