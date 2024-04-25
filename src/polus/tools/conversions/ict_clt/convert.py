"""Convert ICT to CWL CommandLineTool."""

from pathlib import Path
from typing import Union

from ict import ICT, validate


def ict_to_clt(ict_: Union[ICT, Path, str], out_path: Path, network_access: bool = False) -> tuple[dict, Path]:
    """Convert ICT to CWL CommandLineTool and save it to disk."""

    ict_local = ict_ if isinstance(ict_, ICT) else validate(ict_)

    return (ict_local.to_clt(network_access=network_access),
            ict_local.save_clt(out_path, network_access=network_access)
            )

