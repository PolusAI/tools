"""Convert WIPP Plugin to CWL CommandLineTool."""

from pathlib import Path
from typing import Union
from polus.tools.plugins import Plugin
from polus.tools.plugins._plugins.classes import _load_plugin


def wipp_to_clt(wipp: Union[Plugin, Path, str], out_path: Path, network_access: bool = False) -> tuple[dict, Path]:
    """Convert WIPP Plugin to CWL CommandLineTool and save it to disk."""

    plugin = wipp if isinstance(wipp, Plugin) else _load_plugin(wipp)

    return (plugin._to_cwl(network_access=network_access),
            plugin.save_cwl(out_path, network_access=network_access)
            )

