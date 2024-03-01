"""Default id generation functions.

Contains default functions used to generate ids used when building
workflows and their configurations.
"""

from pathlib import Path
from typing import Optional


def generate_cwl_source_repr(step_id: str, io_id: str) -> str:
    """Generate a cwl source representation.

    According to standard, tt should be of the form step/param_id.
    """
    return step_id + "/" + io_id


def generate_worklfow_id(path: Path, id_: str) -> str:
    """Generate an workflow id as an uri."""
    return (path / (id_ + ".cwl")).resolve().as_uri()


def generate_default_step_id(process_name: str) -> str:
    """Default strategy to generate step ids from a process name."""
    return generate_step_id(process_name, prefix="step")


def generate_step_id(
    step_id: str,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
) -> str:
    """Generate step id with optional prefix and/or suffix."""
    if prefix:
        step_id = prefix + "__" + step_id
    if suffix:
        step_id = step_id + "__" + suffix
    return step_id


def generate_workflow_io_id(
    worklflow_id: str,
    step_id: str,
    io_id: str,
) -> str:
    """Generate id for workflow ios. Note that ('/') are forbidden."""
    return worklflow_id + "___" + step_id + "___" + io_id


# TODO remove path arg
def generate_default_input_path(
    step_id: str,
    input_id: str,
    path: Path = Path(),
) -> Path:
    """Generate default input path for synthetic directories or files."""
    # NOTE there is a limitation in cwl that prevents creating nested
    # directories.
    # When copying back staged data, cwl only copies the leaf directory.
    # Name clashes will occur if several inputs have the same name.
    # so we need to create unique directory names for each input.
    return path / (step_id + "__" + input_id)
