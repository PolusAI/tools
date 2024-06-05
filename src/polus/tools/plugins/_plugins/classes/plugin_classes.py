"""Classes for Plugin objects containing methods to configure, run, and save."""

# pylint: disable=W1203, W0212, enable=W1201
import json
import logging
import shutil
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional, Union

from pydantic import ConfigDict

from polus.tools.plugins._plugins.classes.plugin_base import BasePlugin
from polus.tools.plugins._plugins.io._io import DuplicateVersionFoundError, Version
from polus.tools.plugins._plugins.manifests import (
    InvalidManifestError,
    _load_manifest,
    validate_manifest,
)
from polus.tools.plugins._plugins.models import WIPPPluginManifest
from polus.tools.plugins._plugins.utils import name_cleaner

logger = logging.getLogger("polus.plugins")
PLUGINS: dict[str, dict] = {}
# PLUGINS = {"BasicFlatfieldCorrectionPlugin":
#               {Version('0.1.4'): Path(<...>), Version('0.1.5'): Path(<...>)}.
#            "VectorToLabel": {Version(...)}}

"""
Paths and Fields
"""
# Location to store any discovered plugin manifests
_PLUGIN_DIR = Path(__file__).parent.parent.joinpath("manifests")


def refresh() -> None:
    """Refresh the plugin list."""
    organizations = [
        x for x in _PLUGIN_DIR.iterdir() if x.name != "__pycache__" and x.is_dir()
    ]  # ignore __pycache__

    PLUGINS.clear()

    for org in organizations:
        for file in org.iterdir():
            if file.suffix == ".py":
                continue

            try:
                plugin = validate_manifest(file)
            except InvalidManifestError:
                logger.warning(f"Validation error in {file!s}")
            except BaseException as exc:  # pylint: disable=W0718
                logger.warning(f"Unexpected error {exc} with {file!s}")
                raise exc

            else:
                key = name_cleaner(plugin.name)
                # Add version and path to VERSIONS
                if key not in PLUGINS:
                    PLUGINS[key] = {}
                if (
                    plugin.version in PLUGINS[key]
                    and file != PLUGINS[key][plugin.version]
                ):
                    msg = (
                        "Found duplicate version of plugin"
                        f"{plugin.name} in {_PLUGIN_DIR}"
                    )
                    raise DuplicateVersionFoundError(
                        msg,
                    )
                PLUGINS[key][plugin.version] = file


def list_plugins() -> list:
    """List all local plugins."""
    output = list(PLUGINS.keys())
    output.sort()
    return output


class Plugin(WIPPPluginManifest, BasePlugin):
    """WIPP Plugin Class.

    Contains methods to configure, run, and save plugins.

    Attributes:
        versions: A list of local available versions for this plugin.

    Methods:
        save_manifest(path): save plugin manifest to specified path
    """

    id: uuid.UUID  # noqa: A003
    model_config = ConfigDict(extra="allow", frozen=True)

    def __init__(self, _uuid: bool = True, **data: dict) -> None:
        """Init a plugin object from manifest."""
        if _uuid:
            data["id"] = uuid.uuid4()  # type: ignore
        else:
            data["id"] = uuid.UUID(str(data["id"]))  # type: ignore

        data["version"] = Version(data["version"])

        super().__init__(**data)

        self.class_name = name_cleaner(self.name)

        self._io_keys = {i.name: i for i in self.inputs}
        self._io_keys.update({o.name: o for o in self.outputs})

        if not self.author:
            warn_msg = (
                f"The plugin ({self.name}) is missing the author field. "
                "This field is not required but should be filled in."
            )
            logger.warning(warn_msg)

    @property
    def versions(self) -> list:  # cannot be in PluginMethods because PLUGINS lives here
        """Return list of local versions of a Plugin."""
        return list(PLUGINS[self.class_name])

    def save_manifest(
        self,
        path: Union[str, Path],
    ) -> Path:
        """Save plugin manifest to specified path."""
        with Path(path).open("w", encoding="utf-8") as file:
            dict_ = self.manifest
            json.dump(
                dict_,
                file,
                indent=4,
            )

        logger.debug(f"Saved manifest to {Path(path).absolute()}")
        return Path(path).absolute()

    def __setattr__(self, name: str, value: Any) -> None:  # noqa: ANN401
        """Set I/O parameters as attributes."""
        BasePlugin.__setattr__(self, name, value)

    @property
    def _config(self) -> dict:
        model_ = json.loads(self.model_dump_json())
        model_["version"] = model_["version"]["_root"]
        model_["_io_keys"] = deepcopy(self._io_keys)  # type: ignore
        # iterate over I/O to convert to dict
        for io_name, io in model_["_io_keys"].items():
            model_["_io_keys"][io_name] = json.loads(io.model_dump_json())
            # overwrite val if enum
            if io.type.value == "enum":
                model_["_io_keys"][io_name]["value"] = io.value.name  # str
        for inp in model_["inputs"]:
            inp["value"] = None
        for inp in model_["outputs"]:
            inp["value"] = None
        return model_

    def save_config(self, path: Union[str, Path]) -> Path:
        """Save manifest with configured I/O parameters to specified path."""
        with Path(path).open("w", encoding="utf-8") as file:
            json.dump(self._config, file, indent=4, default=str)
        logger.debug(f"Saved config to {Path(path).absolute()}")
        return Path(path).absolute()

    def __repr__(self) -> str:
        """Print plugin name and version."""
        return BasePlugin.__repr__(self)


def _load_plugin(
    manifest: Union[str, dict, Path],
) -> Plugin:
    """Parse a manifest and return Plugin."""
    manifest = _load_manifest(manifest)
    plugin = Plugin(**manifest)  # type: ignore[arg-type]
    return plugin


def submit_plugin(
    manifest: Union[str, dict, Path],
) -> Plugin:
    """Parse a plugin and create a local copy of it.

    This function accepts a plugin manifest as a string, a dictionary (parsed
    json), or a pathlib.Path object pointed at a plugin manifest.

    Args:
        manifest:
            A plugin manifest. It can be a url, a dictionary,
            a path to a JSON file or a string that can be parsed as a dictionary

    Returns:
        A Plugin object populated with information from the plugin manifest.
    """
    plugin = validate_manifest(manifest)
    plugin_name = name_cleaner(plugin.name)

    # Get Major/Minor/Patch versions
    out_name = (
        plugin_name
        + f"_M{plugin.version.major}m{plugin.version.minor}p{plugin.version.patch}.json"
    )

    # Save the manifest if it doesn't already exist in the database
    organization = plugin.containerId.split("/")[0]
    org_path = _PLUGIN_DIR.joinpath(organization.lower())
    org_path.mkdir(exist_ok=True, parents=True)
    if not org_path.joinpath(out_name).exists():
        with org_path.joinpath(out_name).open("w", encoding="utf-8") as file:
            manifest_ = json.loads(plugin.model_dump_json())
            manifest_["version"] = str(plugin.version)
            json.dump(manifest_, file, indent=4)

    # Refresh plugins list
    refresh()
    return _load_plugin(org_path.joinpath(out_name))


def get_plugin(
    name: str,
    version: Optional[Union[str, Version]] = None,
) -> Plugin:
    """Get a plugin with option to specify version.

    Return a plugin with the option to specify a version.
    The specified version's manifest must exist in manifests folder.

    Args:
        name: Name of the plugin.
        version: Optional version of the plugin, must follow semver.

    Returns:
        Plugin
    """
    if version is None:
        return _load_plugin(PLUGINS[name][max(PLUGINS[name])])
    version_ = version if isinstance(version, Version) else Version(version)
    return _load_plugin(PLUGINS[name][version_])


def load_config(config: Union[dict, Path, str]) -> Plugin:
    """Load configured plugin from config file/dict."""
    if isinstance(config, (Path, str)):
        with Path(config).open("r", encoding="utf-8") as file:
            manifest_ = json.load(file)
    elif isinstance(config, dict):
        manifest_ = config
    else:
        msg = "config must be a dict, str, or a path"
        raise TypeError(msg)
    io_keys_ = manifest_["_io_keys"]
    plugin_ = Plugin(_uuid=False, **manifest_)
    for key, value_ in io_keys_.items():
        val = value_["value"]
        if val is not None:  # exclude those values not set
            setattr(plugin_, key, val)
    return plugin_


def remove_plugin(plugin: str, version: Optional[Union[str, list[str]]] = None) -> None:
    """Remove plugin from the local database."""
    if version is None:
        for plugin_version in PLUGINS[plugin]:
            remove_plugin(plugin, plugin_version)
    else:
        if isinstance(version, list):
            for version_ in version:
                remove_plugin(plugin, version_)
            return
        version_ = Version(version) if not isinstance(version, Version) else version
        path = PLUGINS[plugin][version_]
        path.unlink()
    refresh()


def remove_all() -> None:
    """Remove all plugins from the local database."""
    organizations = [
        x for x in _PLUGIN_DIR.iterdir() if x.name != "__pycache__" and x.is_dir()
    ]  # ignore __pycache__
    logger.warning("Removing all plugins from local database")
    for org in organizations:
        shutil.rmtree(org)
    refresh()
