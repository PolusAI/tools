"""Convert WIPP Plugin to ICT."""
from polus.tools.conversions.wipp_to_ict.metadata import convert_wipp_metadata_to_ict
from polus.tools.conversions.wipp_to_ict.hardware import convert_wipp_hardware_to_ict
from polus.tools.conversions.wipp_to_ict.io import convert_wipp_io_to_ict
from polus.tools.conversions.wipp_to_ict.ui import convert_wipp_ui_to_ict
from pathlib import Path
from polus.tools.plugins import Plugin
from polus.tools.plugins._plugins.classes import _load_plugin
from ict import ICT # type: ignore
from typing import Union

def wipp_to_ict(wipp: Union[Plugin, str, Path], out_path: Union[Path, str], **kwargs) -> tuple[ICT, Path]:
    """Convert WIPP Plugin to ICT."""
    plugin = wipp if isinstance(wipp, Plugin) else _load_plugin(wipp)
    metadata = convert_wipp_metadata_to_ict(plugin, **kwargs)
    if plugin.resourceRequirements is not None:
        hardware = convert_wipp_hardware_to_ict(plugin.resourceRequirements)
    else:
        hardware = None
    inputs = [convert_wipp_io_to_ict(inp) for inp in plugin.inputs]
    outputs = [convert_wipp_io_to_ict(out) for out in plugin.outputs]
    ui = [convert_wipp_ui_to_ict(ui_, plugin.inputs) for ui_ in plugin.ui]
    ict_ = ICT(
        **metadata.model_dump(),
        inputs=inputs,
        outputs=outputs,
        ui=ui,
        hardware=hardware,
        )
    return(ict_, ict_.save_yaml(out_path))
