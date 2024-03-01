"""Utils."""

from pathlib import Path

from polus.tools.workflows.exceptions import NotAFileError


def configure_folders(name: str) -> tuple[Path, Path]:
    """Convenience methods to create staging directories.

    Args:
        name: a subdirectory name (usually Path(__file__).stem)

    Returns: a tuple of directories.
        output_dir: can be used to store generated cwl archiving.
        staging_dir: can be used to store temporary files.
    """
    output_dir = (Path() / "cwl_generated" / name).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    staging_dir = (Path() / "tmp" / name).resolve()
    staging_dir.mkdir(parents=True, exist_ok=True)
    return output_dir, staging_dir


def file_exists(path: Path) -> Path:
    """Check whether file exists and return resolved."""
    path = path.resolve()
    if not path.exists():
        msg = f"{path} does not exists."
        raise FileNotFoundError(msg)
    if not path.is_file():
        raise NotAFileError(path)
    return path


def directory_exists(path: Path) -> Path:
    """Check whether the provided path is an existing directory.

    Returns: resolved path.
    Raises: exception is not found or not a file.
    """
    path = path.resolve()
    if not path.exists():
        msg = f"{path} does not exists."
        raise FileNotFoundError(msg)
    if not path.is_dir():
        raise NotADirectoryError(path)
    return path
