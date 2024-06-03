# pylint: disable=no-name-in-module, import-error
"""WIPP UI functions."""

import logging
import re
from typing import Callable, Union

from ict.ui import (
    UICheckbox,
    UIColor,
    UIDatetime,
    UIFile,
    UIItem,
    UIMultiselect,
    UINumber,
    UIPath,
    UISelect,
    UIText,
)

from polus.tools.plugins._plugins.io import Input as WIPPInput  # type: ignore
from polus.tools.plugins._plugins.models.wipp import UI1, UI2  # type: ignore

logger = logging.getLogger("ict")
INPUT_TYPE_TO_UI_TYPE: dict[str, str] = {
    "string": "text",
    "number": "number",
    "boolean": "checkbox",
    "enum": "select",
    "array": "array",  # can be multiselect or just array
    "integer": "number",
}


def _input_type_to_ui_type(input_type: str) -> str:
    """Convert WIPP input type to ICT UI type."""
    if input_type in [
        "collection",
        "pyramid",
        "csvCollection",
        "genericData",
        "stitchingVector",
        "notebook",
        "tensorflowModel",
        "tensorboardLogs",
        "pyramidAnnotation",
    ]:
        return "path"
    return INPUT_TYPE_TO_UI_TYPE[input_type]


def dispatch_ui(ui_type: str) -> Callable:
    """Match UI type (str) to relevant UI Model."""
    if ui_type == "text":
        return UIText
    if ui_type == "number":
        return UINumber
    if ui_type == "checkbox":
        return UICheckbox
    if ui_type == "select":
        return UISelect
    if ui_type == "multiselect":
        return UIMultiselect
    if ui_type == "color":
        return UIColor
    if ui_type == "datetime":
        return UIDatetime
    if ui_type == "file":
        return UIFile
    if ui_type == "path":
        return UIPath
    raise ValueError(f"UI type {ui_type} not found")


def convert_wipp_ui_to_ict(
    wipp_ui: Union[UI1, UI2], wipp_inputs: list[WIPPInput]
) -> UIItem:
    """Convert WIPP UI to ICT."""
    key_ = wipp_ui.key
    title_ = wipp_ui.title
    description_ = wipp_ui.description
    if wipp_ui.condition is not None:
        # match using regex
        condition_regex = re.compile(
            r"(inputs|outputs)\.\w+(==|!=|<|>|<=|>=|&&)'?\w+'?$"
        )
        regex_match = re.search(condition_regex, wipp_ui.condition)
        if regex_match is None:
            logger.warning(
                "Condition statement for %s is not in the correct format,"
                "default template will be used",
                key_,
            )
            condition_ = f"inputs.{key_.split('.')[1]}==value"
        else:  # regex matched
            condition_ = regex_match.group(0)
    else:
        condition_ = None
    if key_ == "fieldsets":
        raise NotImplementedError("fieldsets in UI not implemented")
    else:
        inp_name = key_.split(".")[1]  # inputs.<name>
    relevant_input = [inp for inp in wipp_inputs if inp.name == inp_name]
    if len(relevant_input) == 0:
        raise ValueError(f"UI key {key_} does not match any input name")
    relevant_input = relevant_input[0]
    input_type = relevant_input.type  # type: ignore
    ui_type = _input_type_to_ui_type(input_type)
    if ui_type in ["checkbox", "number"]:
        default_ = wipp_ui.default
        return dispatch_ui(ui_type)(
            key=key_,
            title=title_,
            description=description_,
            condition=condition_,
            default=default_,
            type=ui_type,
        )
    if ui_type in ["select", "multiselect"]:
        if "values" in relevant_input.options.keys():  # type: ignore
            options_ = relevant_input.options["values"]  # type: ignore
            return dispatch_ui(ui_type)(
                key=key_,
                title=title_,
                description=description_,
                condition=condition_,
                fields=options_,
                type=ui_type,
            )
        # possible values are missing
        # change ui_type to text
        ui_type = "text"

    if ui_type == "array":
        if "values" in relevant_input.options.keys():  # type: ignore
            options_ = relevant_input.options["values"]  # type: ignore
            return dispatch_ui("multiselect")(
                key=key_,
                title=title_,
                description=description_,
                condition=condition_,
                fields=options_,
                type=ui_type,
            )
        # change ui_type to text
        ui_type = "text"

    return dispatch_ui(ui_type)(
        key=key_,
        title=title_,
        description=description_,
        condition=condition_,
        type=ui_type,
    )
