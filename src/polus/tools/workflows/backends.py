"""Backends."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

import yaml  # type: ignore[import]

from polus.tools.workflows.logger import get_logger
from polus.tools.workflows.utils import file_exists

logger = get_logger(__name__)


def run_cwl(
    process_file: Path,
    config_file: Optional[Path] = None,
    extra_args: Optional[list[str]] = None,
    cwd: Optional[Path] = None,
    copy_cwl: bool = True,
) -> subprocess.CompletedProcess:
    """Run cwltool with a config file or provided parameters.

    Args:
        process_file:   the cwl file we want to run.
        config_file:    (optional) a config file for this workflow.
        extra_args:     (optional) any additional parameters.
        cwd:            (optional) the directory from which to run the tool.
        copy_cwl:       (optional) whether to copy the original cwl in
                        cwd and use the copy.
    """
    cmd = ["cwltool"]

    if cwd is None:
        cwd = Path()  # by default we run cwltool in the current directory.
    cwd = cwd.resolve()

    # make sure we run a file that exists on disk.
    # TODO CHECK we may want to remove that. cwltool can probably run remote defs!
    file_exists(process_file)

    # if we specify a cwd and the workflow file is not present,
    # make a copy in cwd. This is purely for convenience.
    if copy_cwl and process_file.parent != cwd:
        logger.warning(
            f"workflow cwl file: {process_file.as_posix()}\
            copied to working dir: {cwd}",
        )
        shutil.copy(process_file, cwd)

        process_file = cwd / process_file.name  # use the copy

        # update the id
        with Path.open(process_file) as file:
            spec = yaml.safe_load(file)
            spec["id"] = process_file.as_uri()
        with Path.open(process_file, mode="w") as file:
            file.write(yaml.dump(spec))

    cmd.append(process_file.resolve().as_posix())

    if config_file:
        # we do need the config_file to exist.
        file_exists(config_file)
        # config_file wll often contain relative paths.
        # Those paths will be relative to the config_file location itself.
        # so we need to copy the configuration in cwd and use the copy.
        if config_file.parent != cwd:
            logger.warning(
                f"config file: {config_file.as_posix()} copied to working dir: {cwd}",
            )
            shutil.copy(config_file, cwd)
            config_file = cwd / config_file.name  # use the copy.

        cmd.append(config_file.resolve().as_posix())

    if extra_args:
        cmd = cmd + extra_args

    # TODO REMOVE temp hack for conveniently running
    # those workflows.
    # Figure out how to tell cwl to create the
    # directories first.
    if config_file:
        with Path.open(config_file) as file:
            config = yaml.safe_load(file)
            for input_ in config.values():
                if isinstance(input_, dict) and (
                    input_["class"] == "Directory" or input_["class"] == "File"
                ):
                    location = input_["location"]
                    path = (cwd / location).resolve()
                    if not path.exists():
                        logger.warning(
                            f"create file or directory to run workflow: {path}",
                        )
                        path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Running :  {cmd} in cwd : {cwd}")

    return subprocess.run(
        args=cmd,
        capture_output=False,
        check=True,
        text=True,
        cwd=cwd,
    )
