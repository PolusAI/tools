# pylint: disable=no-name-in-module, import-error
"""Convert from WIPP Plugin Manifest to ICT."""

import logging
import re
from typing import Any, Union

from polus.tools.plugins import Plugin  # type: ignore

from ict.metadata import Metadata as ICTMetadata

logger = logging.getLogger("ict")

SPEC_VERSION = "1.0.0"


def _get_ict_name(container: str, name: str) -> Union[str, None]:
    """Get the name of the ICT from WIPP containerId + WIPP name."""
    try:
        r_s = container.split("/")[0] + "/" + (name.replace(" ", ""))
    except Exception:  # pylint: disable=broad-except
        return None
    return r_s


def _get_ict_author(author: str) -> Union[list[str], None]:
    """Get the author of the ICT from WIPP author."""
    try:
        if "," in author:
            r_s = [" ".join(x.lstrip(" ").split(" ")[0:2]) for x in author.split(",")]
        else:
            r_s = [" ".join(author.split(" ")[0:2])]
    except Exception:  # pylint: disable=broad-except
        return None
    return r_s


def _get_ict_email(author: str) -> Union[str, None]:
    """Get the email for the ICT from WIPP author, if any."""
    email_regex = re.compile(r"[^()\s]+@\S+\.[^()\s.]+")
    emails = email_regex.findall(author)
    if len(emails) > 0:
        return emails[0]
    return None


def convert_wipp_metadata_to_ict(wipp: Plugin, **kwargs) -> ICTMetadata:
    """Convert WIPP Metadata to ICT Metadata."""
    spec_version_ = SPEC_VERSION
    _args_set = {
        "name",
        "version",
        "container",
        "entrypoint",
        "title",
        "description",
        "author",
        "contact",
        "repository",
    }
    _args: dict[str, Any] = {
        "name": None,
        "version": None,
        "container": None,
        "entrypoint": None,
        "title": None,
        "description": None,
        "author": None,
        "contact": None,
        "repository": None,
    }
    _args["name"] = _get_ict_name(wipp.containerId, wipp.title)
    _args["version"] = str(wipp.version)
    _args["container"] = wipp.containerId
    if wipp.baseCommand is not None:
        _args["entrypoint"] = " ".join(wipp.baseCommand)
    _args["title"] = wipp.title
    _args["description"] = wipp.description
    _args["author"] = _get_ict_author(wipp.author)
    _args["contact"] = _get_ict_email(wipp.author)
    _args["repository"] = wipp.repository
    if _args["name"] is None or _args["author"] is None or _args["contact"] is None:
        logger.warning(
            f"Check values of metadata in {wipp.name}. Defaults used for conversion."
        )
    if _args["name"] is None:
        _args["name"] = "organization/ICTname"
    if _args["author"] is None:
        _args["author"] = ["First Last"]
    if _args["contact"] is None:
        _args["contact"] = "author@ict.com"
    if _args["entrypoint"] is None:
        _args["entrypoint"] = "[python3, main.py]"
    if _args["repository"] is None or _args["repository"] == "":
        _args["repository"] = "https://github.com/polusai/image-tools"
    _kwargs_keys = set(kwargs.keys())
    _double_args = _args_set.intersection(_kwargs_keys)
    for arg in _double_args:
        _args[arg] = kwargs[arg]
        kwargs.pop(arg)
    # mypy incorrectly marks
    # optional fields as missing
    return ICTMetadata(  # type: ignore
        specVersion=spec_version_,  # type: ignore
        name=_args["name"],  # type: ignore
        version=_args["version"],  # type: ignore
        container=_args["container"],
        entrypoint=_args["entrypoint"],  # type: ignore
        title=_args["title"],
        description=_args["description"],
        author=_args["author"],  # type: ignore
        contact=_args["contact"],  # type: ignore
        repository=_args["repository"],
        **kwargs,
    )
