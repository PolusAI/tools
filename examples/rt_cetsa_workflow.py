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

WORKFLOW_OUTPUT_DIR = Path(
    "out_analysis",
)  # relative path in the execution directory (cwd)
WORKFLOW_INPUT_DIR = Path(
    "/Users/antoinegerardin//Documents/data/rt-cetsa/20210318 LDHA compound plates/20210318 LDHA compound plate 1 6K cells",  # noqa: E501
)
PLATEMAP_FILE = Path("/Users/antoinegerardin/RT-CETSA-Analysis/data/platemap.xlsx")

if __name__ == "__main__":
    # collect clts
    plate_extraction_cwl = "https://raw.githubusercontent.com/agerardin/image-tools/bf32f5c342ab32108e35eff8cb794b2f1f1e65e8/segmentation/rt-cetsa-plate-extraction-tool/rt_cetsa_plate_extraction.cwl"  # noqa: E501
    intensity_extraction_cwl = "https://raw.githubusercontent.com/agerardin/image-tools/bf32f5c342ab32108e35eff8cb794b2f1f1e65e8/features/rt-cetsa-intensity-extraction-tool/rt_cetsa_intensity_extraction.cwl"  # noqa: E501
    moltenprot_cwl = "https://raw.githubusercontent.com/agerardin/tabular-tools/feat/rt_cetsa_tools/regression/rt-cetsa-moltenprot-tool/rt_cetsa_moltenprot.cwl"  # noqa: E501
    analysis_cwl = "https://raw.githubusercontent.com/agerardin/tabular-tools/feat/rt_cetsa_tools/regression/rt-cetsa-analysis-tool/rt_cetsa_analysis.cwl"  # noqa: E501

    clt_files = [
        plate_extraction_cwl,
        intensity_extraction_cwl,
        moltenprot_cwl,
        analysis_cwl,
    ]

    clts = [CommandLineTool.load(clt) for clt in clt_files]
    steps = [StepBuilder()(clt) for clt in clts]

    plate_extraction, intensity_extraction, moltenprot, analysis = steps

    # Plate Extraction
    plate_extraction.inpDir = WORKFLOW_INPUT_DIR
    plate_extraction.filePattern = "{index:d+}.tif"

    # Intensity Extract
    intensity_extraction.inpDir = plate_extraction.outDir
    intensity_extraction.filePattern = "{index:d+}.ome.tif"

    # Moltenprot
    moltenprot.inpDir = intensity_extraction.outDir
    analysis.inpDir = moltenprot.outDir
    analysis.platemap = PLATEMAP_FILE
    analysis.outDir = WORKFLOW_OUTPUT_DIR

    workflow = WorkflowBuilder(workdir=OUTPUT_DIR)("wf_rt_cetsa", steps=steps)

    pprint([input_.id_ for input_ in workflow.inputs])  # noqa: T203

    config = workflow.save_config(OUTPUT_DIR)

    run_cwl(
        OUTPUT_DIR / f"{workflow.name}.cwl",
        config_file=config,
        cwd=STAGING_DIR,
        cwltool_flags=["--relax-path-checks"],
    )
