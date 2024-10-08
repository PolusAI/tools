"""API to configure and run image-tools."""

import logging

# from pathlib import Path
from typing import Union

from polus.tools.plugins._plugins.classes import Plugin  # pylint: disable=unused-import
from polus.tools.plugins._plugins.classes import (
    _refresh,  # pylint: disable=unused-import
)
from polus.tools.plugins._plugins.classes import (
    get_plugin,  # pylint: disable=unused-import
)
from polus.tools.plugins._plugins.classes import (
    list_plugins,  # pylint: disable=unused-import
)
from polus.tools.plugins._plugins.classes import (
    load_config,  # pylint: disable=unused-import
)
from polus.tools.plugins._plugins.classes import (
    remove_all,  # pylint: disable=unused-import
)
from polus.tools.plugins._plugins.classes import (
    validate_local_manifests,  # pylint: disable=unused-import
)
from polus.tools.plugins._plugins.classes import (  # pylint: disable=unused-import
    remove_plugin,
    submit_plugin,
)
from polus.tools.plugins._plugins.update import (  # pylint: disable=unused-import
    update_nist_plugins,
    update_polus_plugins,
)

logger = logging.getLogger("polus.tools.plugins")

# TODO: manage VERSION

# with Path(__file__).parent.joinpath("_plugins/VERSION").open(
#     "r",
#     encoding="utf-8",
# ) as version_file:
#     VERSION = version_file.read().strip()


_refresh(supress_warnings=True)  # calls the refresh method when library is imported


def __getattr__(name: str) -> Union[Plugin, list]:
    if name == "list":
        return list_plugins()
    if name in list_plugins():
        return get_plugin(name)
    msg = f"module '{__name__}' has no attribute '{name}'"
    raise AttributeError(msg)


__all__ = [
    "submit_plugin",
    "get_plugin",
    "load_config",
    "list_plugins",
    "validate_local_manifests",
    "update_polus_plugins",
    "update_nist_plugins",
    "remove_all",
    "remove_plugin",
]
