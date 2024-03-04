"""Test model roundtrip to check there is no loss of information
when serializing our models.
"""

import pytest
import yaml
from pathlib import Path
import filecmp
import cwl_utils.parser as cwl_parser

from polus.tools.workflows import CommandLineTool, Workflow
from polus.tools.workflows.utils import configure_folders

FILE_NAME = Path(__file__).stem
OUTPUT_DIR, STAGING_DIR = configure_folders(FILE_NAME)


# NOTE yaml multilines is not consistently implemented.
# cwl-utils use ruamel rather than PyYaml and do some configuration.
# For now we deal with it the PyYaml way, which can lead to
# some inconsistencies in the roudntrip test results.
@pytest.mark.parametrize("filename", ["echo_string_with_multiline_doc.cwl"])
def test_parsing_doc_with_special_character_string(
    test_data_dir: Path, tmp_dir: Path, filename: str
) -> None:
    """Test roundtrip for clts."""
    __test_roundtrip(tmp_dir, test_data_dir, filename)


@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_clt_roundtrip(test_data_dir: Path, tmp_dir: Path, filename: str) -> None:
    """Test roundtrip for clts."""
    __test_roundtrip(tmp_dir, test_data_dir, filename)


@pytest.mark.parametrize("filename", ["workflow3.cwl"])
def test_workflow_roundtrip(test_data_dir: Path, tmp_dir: Path, filename: str) -> None:
    """Test roundtrip for workflows."""
    __test_roundtrip(tmp_dir, test_data_dir, filename)


def __test_roundtrip(tmp_dir: Path, test_data_dir: Path, filename: str) -> None:
    """Test model roundtrip.

    Test model roundtrip to check there is no loss of information
    when serializing our models.
    """
    cwl_file = test_data_dir / filename

    # standardized ref file from cwlparser
    ref_filepath = Path(tmp_dir) / f"ref_{cwl_file.stem}.cwl"
    ref_model = cwl_parser.load_document_by_uri(cwl_file)
    serialized_ref_model = cwl_parser.save(ref_model)
    with ref_filepath.open("w", encoding="utf-8") as ref_file:
        ref_file.write(yaml.dump(serialized_ref_model))

    # read cwl and dump model
    if ref_model.class_ == "CommandLineTool":
        new_model = CommandLineTool.load(cwl_file)
    elif ref_model.class_ == "Workflow":
        new_model = Workflow.load(cwl_file)
    else:
        raise Exception
    new_model.save(OUTPUT_DIR)
    new_model_file = new_model.save(tmp_dir)
    roundtrip_model = cwl_parser.load_document_by_uri(new_model_file)
    serialized_roundtrip_model = cwl_parser.save(roundtrip_model)

    # write model
    roundtrip_filepath = Path(tmp_dir) / "round_trip_echo_string.cwl"
    with roundtrip_filepath.open("w", encoding="utf-8") as roundtrip_file:
        roundtrip_file.write(yaml.dump(serialized_roundtrip_model))

    # make sure ref and dumped model are identical
    assert filecmp.cmp(ref_filepath, roundtrip_filepath, shallow=False)
