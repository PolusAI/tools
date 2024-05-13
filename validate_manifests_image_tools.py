"""Script to validate image tools manifests."""

# pylint: disable=W0718, W1203
import logging
from pathlib import Path

import typer

from polus.tools.plugins._plugins.manifests import validate_manifest

app = typer.Typer(help="Validate image tools manifests.")
fhandler = logging.FileHandler("validate_manifests_image_tools.log")
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
logger = logging.getLogger("validate_image_tools")
logger.addHandler(fhandler)


@app.command()
def main(
    repo: Path = typer.Option(
        None,
        "--repo",
        "-r",
        help="Path to the image-tools repository.",
    )
) -> None:
    """Validate image-tools manifests."""
    local_manifests = list(repo.rglob("*plugin.json"))
    ignore_list = ["cookiecutter", ".env"]
    local_manifests = [
        x for x in local_manifests if not any(ig in str(x) for ig in ignore_list)
    ]
    n = len(local_manifests)
    n_bad = 0
    logger.info(f"Found {n} manifests in {repo}")
    for manifest in local_manifests:
        try:
            validate_manifest(manifest)
        except BaseException:
            n_bad += 1
            logger.error(f"Invalid {manifest}: ", exc_info=True)
    logger.info(f"{n-n_bad}/{n} manifests are valid. See logs for more info.")


if __name__ == "__main__":
    app()
