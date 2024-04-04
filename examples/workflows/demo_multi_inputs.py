"""Test loading and serializing optional types."""

from pathlib import Path

from polus.tools.workflows import Process
from polus.tools.workflows.backends import run_cwl
from polus.tools.workflows.builders import StepBuilder
from polus.tools.workflows.logger import get_logger
from polus.tools.workflows.utils import configure_folders

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)

logger = get_logger(__name__)

test_data_dir = Path("tests") / "workflows" / "test_data"
filename = "multi-inputs-workflow.cwl"

cwl_file = test_data_dir / filename
wf = Process.load(cwl_file)

wf_step = StepBuilder()(wf)
wf_step.msg1 = "hello"
wf_step.msg2 = "world"

# save files
wf_file = wf.save(OUTPUT_DIR)
config_file = wf_step.save_config(OUTPUT_DIR)

# execute locally
run_cwl(wf_file, config_file=config_file, cwd=STAGING_DIR)
