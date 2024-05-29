# ruff: noqa
"""Script to convert all WIPP manifests to CLT.

Example:
```bash
python wipp_to_clt.py --repo /path/to/repo --all
```
"""

# pylint: disable=W0718, W1203
import logging
from pathlib import Path

import typer
from tqdm import tqdm

from polus.tools.conversions import wipp_to_clt
from polus.tools.plugins._plugins.classes import _load_plugin
from polus.tools.plugins._plugins.utils import name_cleaner

app = typer.Typer(help="Convert WIPP manifests to CLT.")
fhandler = logging.FileHandler("wipp_to_clt_conversion.log")
fformat = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
)
fhandler.setFormatter(fformat)
fhandler.setLevel("INFO")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
logger = logging.getLogger("wipp_to_clt")
logger.addHandler(fhandler)


@app.command()
def main(
    repo: Path = typer.Option(
        None,
        "--repo",
        "-r",
        help="Path to the repository containing the WIPP manifests.",
    ),
    all_: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Convert all manifests in the repository.",
    ),
    name: str = typer.Option(
        None,
        "--name",
        "-n",
        help="Name of the plugin to convert.",
    ),
) -> None:
    """Convert WIPP manifests to CLT."""
    local_manifests = list(repo.rglob("*plugin.json"))
    logger.info(f"Found {len(local_manifests)} manifests in {repo}")
    ignore_list = ["cookiecutter", ".env", "Shared-Memory-OpenMP"]
    # Shared-Memory-OpenMP ignored for now until version
    # and container are fixed in the manifest
    local_manifests = [
        x for x in local_manifests if not any(ig in str(x) for ig in ignore_list)
    ]
    problems = {}
    converted = 0
    if not all_ and name is None:
        logger.error("Please provide a name if not converting all manifests.")
        raise typer.Abort
    if name is not None:
        if all_:
            logger.warning("Ignoring --all flag since a name was provided.")
        logger.info(f"name: {name}")
        all_ = False
    logger.info(f"all: {all_}")
    if all_:
        n = len(local_manifests)
        for manifest in tqdm(local_manifests):
            try:
                name_ = name_cleaner(_load_plugin(manifest).name)
                wipp_to_clt(manifest, manifest.with_name(f"{name_}.cwl"))
                converted += 1

            except BaseException as e:
                problems[Path(manifest).parts[4:-1]] = str(e)
    if name is not None:
        n = 1
        for manifest in [x for x in local_manifests if name in str(x)]:
            try:
                name_ = name_cleaner(_load_plugin(manifest).name)
                wipp_to_clt(manifest, manifest.with_name(f"{name_}.cwl"))
                converted += 1

            except BaseException as e:
                problems[Path(manifest).parts[4:-1]] = str(e)

    logger.info(f"Converted {converted}/{n} plugins")
    if len(problems) > 0:
        logger.error(f"Problems: {problems}")
        logger.info(f"There were {len(problems)} problems in {n} manifests.")


if __name__ == "__main__":
    app()
