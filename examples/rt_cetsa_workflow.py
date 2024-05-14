"""Example of an image processing workflow."""

from pathlib import Path
from pprint import pprint

from polus.tools.workflows import CommandLineTool
from polus.tools.workflows import StepBuilder
from polus.tools.workflows import WorkflowBuilder
from polus.tools.workflows import run_cwl
from polus.tools.workflows.utils import configure_folders

CWLTOOL_PATH = Path() / "cwl/rt_cetsa"  # clts we will use

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)

WORKFLOW_OUTPUT_DIR = Path("out")  # relative path in the execution directory (cwd)
WORKFLOW_INPUT_DIR = Path(
    "/Users/antoinegerardin//Documents/data/rt-cetsa/20210318 LDHA compound plates/20210318 LDHA compound plate 1 6K cells",  # noqa: E501
)

if __name__ == "__main__":
    # collect clts
    moltenprot_cwl = "/Users/antoinegerardin/Documents/projects/tabular-tools/regression/rt-cetsa-moltprot-tool/rt_cetsa_moltenprot.cwl"  # noqa: E501
    plate_extraction_cwl = "/Users/antoinegerardin/Documents/projects/polus-plugins/segmentation/rt-cetsa-plate-extraction-tool/rt_cetsa_plate_extraction.cwl"  # noqa: E501

    clt_files = [plate_extraction_cwl]

    clts = [CommandLineTool.load(clt) for clt in clt_files]
    steps = [StepBuilder()(clt) for clt in clts]

    plate_extraction = steps[0]

    # Plate Extraction
    plate_extraction.inpDir = WORKFLOW_INPUT_DIR
    plate_extraction.filePattern = "{index:d+}.tif"
    plate_extraction.outDir = WORKFLOW_OUTPUT_DIR

    # Moltenprot
    # moltenprot.inpDir =

    workflow = WorkflowBuilder(workdir=OUTPUT_DIR)("wf_rt_cetsa", steps=steps)

    pprint([input_.id_ for input_ in workflow.inputs])  # noqa: T203

    config = workflow.save_config(OUTPUT_DIR)

    run_cwl(
        OUTPUT_DIR / f"{workflow.name}.cwl",
        config_file=config,
        cwd=STAGING_DIR,
        cwltool_flags=["--relax-path-checks"],
    )
