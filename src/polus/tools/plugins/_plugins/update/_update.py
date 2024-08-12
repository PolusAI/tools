# pylint: disable=W1203, W1201
import json
import logging
import re
import typing

from pydantic import ValidationError
from tqdm import tqdm  # type: ignore

from polus.tools.plugins._plugins.classes import (
    _private_submit_plugin_for_update,
    _refresh,
    submit_plugin,
)
from polus.tools.plugins._plugins.gh import _init_github
from polus.tools.plugins._plugins.io import Version
from polus.tools.plugins._plugins.manifests import (
    InvalidManifestError,
    _error_log,
    _scrape_manifests,
)

logger = logging.getLogger("polus.plugins")


def update_polus_plugins(
    gh_auth: typing.Optional[str] = None,
    min_depth: int = 2,
    max_depth: int = 3,
) -> None:
    """Scrape PolusAI/image-tools GitHub repo and create local versions of Plugins found.

    Args:
        gh_auth:
            GitHub authentication token, if empty will try
            to get it from the environment variable GITHUB_AUTH,
            otherwise will connect without authentication.
        min_depth: Minimum depth to scrape, default is 2
        max_depth: Maximum depth to scrape, default is 3

    """
    logger.info("Updating polus plugins.")
    # Get all manifests
    valid, invalid = _scrape_manifests(
        "polusai/image-tools",
        _init_github(gh_auth),
        min_depth,
        max_depth,
        True,
    )
    manifests = valid.copy()
    manifests.extend(invalid)
    logger.info(f"Submitting {len(manifests)} plugins.")

    for manifest in manifests:
        try:
            plugin = _private_submit_plugin_for_update(manifest, return_plugin=True)
            # plugin is of type Plugin since return_plugin = True
            # but mypy does not recognize this

            # # Check that plugin version matches container version tag
            container_name, version = tuple(
                plugin.containerId.split(":")  # type: ignore # pylint: disable=E1101
            )
            version = Version(version)
            organization, container_name = tuple(container_name.split("/"))
            if plugin.version != version:  # type: ignore
                raise InvalidManifestError("containerId")

            # Check to see that the plugin is registered to Labshare
            if organization not in ["polusai", "labshare"]:
                raise InvalidManifestError("organization")

        except InvalidManifestError as im_err:
            if im_err.__cause__ is not None:
                logger.error(
                    f"Validation error in {manifest['name']}: {im_err.__cause__}"
                )
            else:
                if "name" not in manifest:
                    logger.error(f"Validation error in {manifest}: no value for 'name'")
                if "containerId" in im_err.args[0]:
                    msg = (
                        f"In {manifest['name']}:"
                        f"containerId version ({version}) does not "  # type: ignore
                        f"match plugin version ({plugin.version})"  # type: ignore
                    )
                    logger.error(msg)
                if "organization" in im_err.args[0]:
                    msg = (
                        f"In {manifest['name']}:"
                        "all polus plugin containers must be"
                        " under the Labshare organization."
                    )
                    logger.error(msg)

        except Exception as exc:  # pylint: disable=W0718
            if "name" in manifest:
                logger.error(f"Error in {manifest['name']}: {exc}")
            else:
                logger.error(f"Error in {manifest}: {exc}")

    _refresh(supress_warnings=True)


def update_nist_plugins(gh_auth: typing.Optional[str] = None) -> None:
    """Scrape NIST GitHub repo and create local versions of Plugins."""
    # Parse README links
    gh = _init_github(gh_auth)
    repo = gh.get_repo("usnistgov/WIPP")
    contents = repo.get_contents("plugins")
    readme = [r for r in contents if r.name == "README.md"][0]
    pattern = re.compile(
        r"\[manifest\]\((https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))\)",
    )
    matches = pattern.findall(str(readme.decoded_content))
    logger.info("Updating NIST plugins.")
    for match in tqdm(matches, desc="NIST Manifests"):
        url_parts = match[0].split("/")[3:]
        plugin_repo = gh.get_repo("/".join(url_parts[:2]))
        manifest = json.loads(
            plugin_repo.get_contents("/".join(url_parts[4:])).decoded_content,
        )

        try:
            _private_submit_plugin_for_update(manifest)

        except ValidationError as val_err:
            logger.error(f"Validation error in {manifest['name']}: {val_err}")

        except InvalidManifestError as im_err:
            logger.error(f"Validation error in {manifest['name']}: {im_err.__cause__}")

        except Exception as exc:  # pylint: disable=W0718
            logger.error(f"Error in {manifest['name']}: {exc}")
    _refresh(supress_warnings=True)
