"""Convert WIPP Plugin to ICT."""
from polus.tools.conversions.wipp_to_ict.metadata import convert_wipp_metadata_to_ict
from polus.tools.conversions.wipp_to_ict.hardware import convert_wipp_hardware_to_ict
from polus.tools.conversions.wipp_to_ict.io import convert_wipp_io_to_ict
from polus.tools.conversions.wipp_to_ict.ui import convert_wipp_ui_to_ict
from functools import singledispatch
from pathlib import Path
from polus.tools.plugins import Plugin
from polus.tools.plugins._plugins.classes import _load_plugin
from ict import ICT # type: ignore
from typing import Union

@singledispatch
def wipp_to_ict(wipp: Plugin, out_path: Union[Path, str], **kwargs) -> tuple[ICT, Path]:
    """Convert WIPP Plugin to ICT."""
    metadata = convert_wipp_metadata_to_ict(wipp, **kwargs)
    if wipp.resourceRequirements is not None:
        hardware = convert_wipp_hardware_to_ict(wipp.resourceRequirements)
    else:
        hardware = None
    inputs = [convert_wipp_io_to_ict(inp) for inp in wipp.inputs]
    outputs = [convert_wipp_io_to_ict(out) for out in wipp.outputs]
    ui = [convert_wipp_ui_to_ict(ui_, wipp.inputs) for ui_ in wipp.ui]
    ict_ = ICT(
        **metadata.model_dump(),
        inputs=inputs,
        outputs=outputs,
        ui=ui,
        hardware=hardware,
        )
    return(ict_, ict_.save_yaml(out_path))

@wipp_to_ict.register(Path)  # type: ignore
def _(wipp, out_path, **kwargs) -> tuple[ICT, Path]:
    """Convert WIPP Plugin to ICT."""
    wipp_ = _load_plugin(wipp)
    return wipp_to_ict(wipp_, out_path, **kwargs)

@wipp_to_ict.register(str)  # type: ignore
def _( wipp, out_path, **kwargs) -> tuple[ICT, Path]:
    """Convert WIPP Plugin to ICT."""
    wipp_ = _load_plugin(wipp)
    return wipp_to_ict(wipp_, out_path, **kwargs)