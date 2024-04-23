# pylint: disable=no-name-in-module, import-error
"""WIPP I/O functions."""

from typing import Union

from polus.tools.plugins._plugins.io import Input, Output  # type: ignore

from ict.io import IO

WIPP_IO_DICT: dict[str, str] = {
    "string": "string",
    "boolean": "boolean",
    "number": "number",
    "integer": "number",
    "array": "array",
    "enum": "string",
}


def _wipp_to_ict_type(wipp_type: str) -> str:
    """Map WIPP I/O type to ICT I/O type."""
    if wipp_type in WIPP_IO_DICT:
        return WIPP_IO_DICT[wipp_type]
    return "path"  # default to path


def convert_wipp_io_to_ict(wipp: Union[Input, Output]) -> IO:
    """Convert WIPP I/O to ICT."""
    name_ = wipp.name
    type_ = _wipp_to_ict_type(wipp.type)
    description_ = wipp.description
    if isinstance(wipp, Input):
        required_ = wipp.required
    else:
        # output default to required
        required_ = True
    if wipp.options is not None and "format" in wipp.options:
        format_ = [wipp.options["format"]]
    else:
        # default to [<wipp type>] just for conversion
        format_ = [wipp.type]
    if description_ is None:
        description_ = ""
    name_ = name_.replace("_", "")  # ICT does not allow underscores in names
    return IO(
        name=name_,
        type=type_,  # type: ignore
        description=description_,
        required=required_,
        format=format_,
    )
