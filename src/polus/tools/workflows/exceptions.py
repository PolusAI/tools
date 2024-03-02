"""Exceptions."""

from pathlib import Path
from typing import Union

from polus.tools.workflows.types import CWLType
from polus.tools.workflows.types import PythonValue


class NotAFileError(Exception):
    """Raised if path is not a file."""

    def __init__(self, path: Path) -> None:
        """Init NotAFileError."""
        super().__init__(f"{path} is not a file.")


class IncompatibleTypeError(Exception):
    """Raised if types are incompatible."""

    def __init__(self, type1: CWLType, type2: CWLType) -> None:
        """Init IncompatibleTypeError."""
        super().__init__(f"{type1} != {type2}")


class UnexpectedTypeError(Exception):
    """Raised if type is not supported."""

    def __init__(self, type_: CWLType) -> None:
        """Init UnexpectedTypeError."""
        super().__init__(f"unexpected type : {type_}")


class IncompatibleValueError(Exception):
    """Raised if value cannot be assigned to a type."""

    def __init__(self, io_id: str, type_: CWLType, value: PythonValue) -> None:
        """Init IncompatibleValueError."""
        super().__init__(
            f'Cannot assign value: "{value}"\
            to parameter: "{io_id}"\
            of type: "{type_}"',
        )


class CannotParseAdditionalInputParamError(Exception):
    """Raised if the model for an additional input is not valid."""

    pass


class UnsupportedProcessClassError(Exception):
    """Raised if the cwl process type is not supported."""

    def __init__(self, class_: str) -> None:
        """Init UnsupportedProcessClassError."""
        super().__init__(f"unsupported cwl process class : {class_}")


class BadCwlProcessFileError(Exception):
    """Raised if the cwl process file cannot be parsed."""

    def __init__(self, cwl_file: Union[Path, str]) -> None:
        """Init BadCwlProcessFileError."""
        if isinstance(cwl_file, Path):
            cwl_file = cwl_file.as_posix()
        super().__init__(f"Invalid cwl file : {cwl_file}")


class UnsupportedCaseError(Exception):
    """Raise if we have a logic error or did not anticipate a use case."""

    pass


class WhenClauseValidationError(Exception):
    """WhenClauseValidationError.

    Raise whenever the when clause is invalid.
    """

    pass
