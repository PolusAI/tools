"""Utilities for manifest parsing and validation."""

import json
import logging
import pathlib
from typing import Optional, Union

import github
import requests  # type: ignore
import validators  # type: ignore
from pydantic import ValidationError, errors
from tqdm import tqdm  # type: ignore

from polus.tools.plugins._plugins.io import Version
from polus.tools.plugins._plugins.models import WIPPPluginManifest

logger = logging.getLogger("polus.plugins")

# Fields that must be in a plugin manifest
REQUIRED_FIELDS = [
    "name",
    "version",
    "description",
    "author",
    "containerId",
    "inputs",
    "outputs",
    "ui",
]


class InvalidManifestError(Exception):
    """Raised when manifest has validation errors."""


def is_valid_manifest(plugin: dict) -> bool:
    """Validate basic attributes of a plugin manifest.

    Args:
        plugin: a parsed plugin json file

    Returns:
        `True` if the plugin has the minimal json fields
    """
    fields = set(plugin.keys())
    required_fields = set(REQUIRED_FIELDS)

    diff = required_fields - fields
    if len(diff) > 0:
        if "name" in fields:
            msg = f"missing json fields {diff} in {plugin['name']}."
        elif "title" in fields:
            msg = f"missing json fields {diff} in {plugin['title']}."
        else:
            msg = f"missing json fields {diff} in {plugin}."
        logger.error(msg)
        return False
    return True


def _load_manifest(manifest: Union[str, dict, pathlib.Path]) -> dict:
    """Return manifest as dict from str (url or path) or pathlib.Path."""
    if isinstance(manifest, dict):  # is dict
        return manifest
    if isinstance(manifest, pathlib.Path):  # is path
        if manifest.suffix != ".json":
            msg = "plugin manifest must be a json file with .json extension."
            raise ValueError(msg)

        with manifest.open("r", encoding="utf-8") as manifest_json:
            manifest_ = json.load(manifest_json)
    elif isinstance(manifest, str):  # is str
        if validators.url(manifest):  # is url
            manifest_ = requests.get(manifest, timeout=10).json()
        else:  # could (and should) be path
            try:
                manifest_ = _load_manifest(pathlib.Path(manifest))
            except Exception as exc:  # was not a Path? # noqa
                msg = "invalid manifest"
                raise ValueError(msg) from exc
    else:  # is not str, dict, or path
        msg = f"invalid manifest type {type(manifest)}"
        raise ValueError(msg)
    return manifest_


def validate_manifest(
    manifest: Union[str, dict, pathlib.Path],
) -> WIPPPluginManifest:
    """Validate a plugin manifest against schema."""
    manifest = _load_manifest(manifest)
    manifest["version"] = Version(manifest["version"])  # noqa
    if not "name" in manifest:
        msg = f"{manifest} has no value for name"
        raise InvalidManifestError(msg)

    # Parse the manifest
    try:
        plugin = WIPPPluginManifest(**manifest)
    except ValidationError as e:
        msg = f"{manifest['name']} does not conform to schema"
        raise InvalidManifestError(
            msg,
        ) from e
    except BaseException as e:
        raise e
    return plugin


def _scrape_manifests(
    repo: Union[str, github.Repository.Repository],  # type: ignore
    gh: github.Github,
    min_depth: int = 1,
    max_depth: Optional[int] = None,
    return_invalid: bool = False,
) -> Union[list, tuple[list, list]]:
    if max_depth is None:
        max_depth = min_depth
        min_depth = 0

    if not max_depth >= min_depth:
        msg = "max_depth is smaller than min_depth"
        raise ValueError(msg)

    if isinstance(repo, str):
        repo = gh.get_repo(repo)

    contents = list(repo.get_contents(""))  # type: ignore
    next_contents: list = []
    valid_manifests: list = []
    invalid_manifests: list = []

    for d in range(0, max_depth):
        for content in tqdm(contents, desc=f"{repo.full_name}: {d}"):
            if content.type == "dir":
                next_contents.extend(repo.get_contents(content.path))  # type: ignore
            elif content.name.endswith("plugin.json") and d >= min_depth:
                if "cookiecutter" in content.name:
                    continue
                manifest = json.loads(content.decoded_content)
                if is_valid_manifest(manifest):
                    valid_manifests.append(manifest)
                else:
                    invalid_manifests.append(manifest)

        contents = next_contents.copy()
        next_contents = []

    if return_invalid:
        return valid_manifests, invalid_manifests
    return valid_manifests


def _error_log(val_err: ValidationError, manifest: dict, fct: str) -> None:
    report = []

    for error in val_err.args[0]:
        if isinstance(error, list):
            error = error[0]  # noqa

        if isinstance(error, AssertionError):
            msg = (
                f"The plugin ({manifest['name']}) "
                "failed an assertion check: {err.args[0]}"
            )
            report.append(msg)
            logger.critical(f"{fct}: {report[-1]}")  # pylint: disable=W1203
        elif isinstance(error.exc, errors.MissingError):
            msg = (
                f"The plugin ({manifest['name']}) "
                "is missing fields: {err.loc_tuple()}"
            )
            report.append(msg)
            logger.critical(f"{fct}: {report[-1]}")  # pylint: disable=W1203
        elif errors.ExtraError:
            if error.loc_tuple()[0] in ["inputs", "outputs", "ui"]:
                manifest_ = manifest[error.loc_tuple()[0]][error.loc_tuple()[1]]["name"]
                msg = (
                    f"The plugin ({manifest['name']}) "
                    "had unexpected values in the "
                    f"{error.loc_tuple()[0]} "
                    f"({manifest_}): "
                    f"{error.exc.args[0][0].loc_tuple()}"
                )
                report.append(msg)
            else:
                msg = (
                    f"The plugin ({manifest['name']}) "
                    "had an error: {err.exc.args[0][0]}"
                )
                report.append(msg)
            logger.critical(f"{fct}: {report[-1]}")  # pylint: disable=W1203
        else:
            str_val_err = str(val_err).replace("\n", ", ").replace("  ", " ")
            msg = (
                f"{fct}: Uncaught manifest error in ({manifest['name']}): "
                f"{str_val_err}"
            )
            logger.warning(msg)
