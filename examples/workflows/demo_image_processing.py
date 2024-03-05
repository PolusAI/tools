"""Example of an image processing workflow."""

from pathlib import Path
from pprint import pprint

from polus.tools.workflows import CommandLineTool
from polus.tools.workflows import StepBuilder
from polus.tools.workflows import WorkflowBuilder
from polus.tools.workflows import run_cwl
from polus.tools.workflows.utils import configure_folders

CWLTOOL_PATH = Path() / "cwl/image_tools"  # clts we will use

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)

WORKFLOW_OUTPUT_DIR = Path("out")  # relative path in the execution directory (cwd)

if __name__ == "__main__":
    # collect clts
    bbbc_cwl = CWLTOOL_PATH / "BbbcDownload.cwl"
    rename_cwl = CWLTOOL_PATH / "FileRenaming.cwl"
    ome_converter_cwl = CWLTOOL_PATH / "OmeConverter.cwl"
    montage_cwl = CWLTOOL_PATH / "Montage.cwl"
    image_assembler_cwl = CWLTOOL_PATH / "ImageAssembler.cwl"
    precompute_slide_cwl = CWLTOOL_PATH / "PrecomputeSlide.cwl"

    clt_files = [
        bbbc_cwl,
        rename_cwl,
        ome_converter_cwl,
        montage_cwl,
        image_assembler_cwl,
        precompute_slide_cwl,
    ]
    clts = [CommandLineTool.load(clt) for clt in clt_files]
    steps = [StepBuilder()(clt) for clt in clts]

    (bbbc, rename, ome_converter, montage, image_assembler, precompute_slide) = steps

    # BbbcDownload
    bbbc.name = "BBBC001"

    # FileRenaming
    rename.filePattern = ".*_{row:c}{col:dd}f{f:dd}d{channel:d}.tif"
    rename.outFilePattern = "x{row:dd}_y{col:dd}_p{f:dd}_c{channel:d}.tif"
    rename.mapDirectory = "map"
    rename.inpDir = bbbc.outDir

    # OmeConverter
    ome_converter.filePattern = ".*.tif"
    ome_converter.fileExtension = ".ome.tif"
    ome_converter.inpDir = rename.outDir

    # Montage
    montage.inpDir = ome_converter.outDir
    montage.filePattern = "d1_x00_y03_p{p:dd}_c0.ome.tif"
    montage.layout = "p"

    # ImageAssembler
    image_assembler.imgPath = ome_converter.outDir
    image_assembler.stitchPath = montage.outDir

    # PrecomputeSlide
    precompute_slide.filePattern = ".*.ome.tif"
    precompute_slide.pyramidType = "Zarr"
    precompute_slide.imageType = "Intensity"
    precompute_slide.inpDir = image_assembler.outDir
    precompute_slide.outDir = WORKFLOW_OUTPUT_DIR

    workflow = WorkflowBuilder(workdir=OUTPUT_DIR)("wf_image_processing", steps=steps)

    pprint([input_.id_ for input_ in workflow.inputs])  # noqa: T203

    config = workflow.save_config(OUTPUT_DIR)

    run_cwl(OUTPUT_DIR / f"{workflow.name}.cwl", config_file=config, cwd=STAGING_DIR)
