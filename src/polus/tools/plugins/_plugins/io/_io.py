# type: ignore
# ruff: noqa: S101, A003
# pylint: disable=no-self-argument, C0412
"""Plugins I/O utilities."""
import enum
import logging
import pathlib
import re
from functools import singledispatch, singledispatchmethod
from itertools import zip_longest
from typing import Any, Optional, TypeVar, Union

import fsspec
from pydantic import BaseModel, Field, PrivateAttr
from pydantic.dataclasses import dataclass
from typing_extensions import Annotated

from polus.tools.plugins._plugins._compat import PYDANTIC_V2

if PYDANTIC_V2:
    from typing import Annotated

    from pydantic import RootModel, StringConstraints, field_validator, model_validator
    from pydantic.functional_validators import AfterValidator
else:
    from pydantic import constr, validator

logger = logging.getLogger("polus.plugins")

"""
Enums for validating plugin input, output, and ui components.
"""
WIPP_TYPES = {
    "collection": pathlib.Path,
    "pyramid": pathlib.Path,
    "csvCollection": pathlib.Path,
    "genericData": pathlib.Path,
    "stitchingVector": pathlib.Path,
    "notebook": pathlib.Path,
    "tensorflowModel": pathlib.Path,
    "tensorboardLogs": pathlib.Path,
    "pyramidAnnotation": pathlib.Path,
    "integer": int,
    "number": float,
    "string": str,
    "boolean": bool,
    "array": str,
    "enum": enum.Enum,
    "path": pathlib.Path,
}


class InputTypes(str, enum.Enum):  # wipp schema
    """Enum of Input Types for WIPP schema."""

    COLLECTION = "collection"
    PYRAMID = "pyramid"
    CSVCOLLECTION = "csvCollection"
    GENERICDATA = "genericData"
    STITCHINGVECTOR = "stitchingVector"
    NOTEBOOK = "notebook"
    TENSORFLOWMODEL = "tensorflowModel"
    TENSORBOARDLOGS = "tensorboardLogs"
    PYRAMIDANNOTATION = "pyramidAnnotation"
    INTEGER = "integer"
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    ARRAY = "array"
    ENUM = "enum"


class OutputTypes(str, enum.Enum):  # wipp schema
    """Enum for Output Types for WIPP schema."""

    COLLECTION = "collection"
    PYRAMID = "pyramid"
    CSVCOLLECTION = "csvCollection"
    GENERICDATA = "genericData"
    STITCHINGVECTOR = "stitchingVector"
    NOTEBOOK = "notebook"
    TENSORFLOWMODEL = "tensorflowModel"
    TENSORBOARDLOGS = "tensorboardLogs"
    PYRAMIDANNOTATION = "pyramidAnnotation"


def _in_old_to_new(old: str) -> str:  # map wipp InputType to compute schema's InputType
    """Map an InputType from wipp schema to one of compute schema."""
    d = {"integer": "number", "enum": "string"}
    if old in ["string", "array", "number", "boolean"]:
        return old
    if old in d:
        return d[old]  # integer or enum
    return "path"  # everything else


def _ui_old_to_new(old: str) -> str:  # map wipp InputType to compute schema's UIType
    """Map an InputType from wipp schema to a UIType of compute schema."""
    type_dict = {
        "string": "text",
        "boolean": "checkbox",
        "number": "number",
        "array": "text",
        "integer": "number",
    }
    if old in type_dict:
        return type_dict[old]
    return "text"


FileSystem = TypeVar("FileSystem", bound=fsspec.spec.AbstractFileSystem)


class IOBase(BaseModel):  # pylint: disable=R0903
    """Base Class for I/O arguments."""

    type: Any = None
    options: Optional[dict] = None
    value: Optional[Any] = None
    id_: Optional[Any] = None
    _fs: Optional[FileSystem] = PrivateAttr(
        default=None,
    )  # type checking is done at plugin level

    def _validate(self) -> None:  # pylint: disable=R0912
        value = self.value

        if value is None:
            if self.required:
                msg = f"""
                The input value ({self.name}) is required,
                but the value was not set."""
                raise TypeError(
                    msg,
                )

            return

        if self.type == InputTypes.ENUM:
            try:
                if isinstance(value, str):
                    value = enum.Enum(self.name, self.options["values"])[value]
                elif not isinstance(value, enum.Enum):
                    raise ValueError

            except KeyError:
                logging.error(
                    f"""
                    Value ({value}) is not a valid value
                    for the enum input ({self.name}).
                    Must be one of {self.options['values']}.
                    """,
                )
                raise
        else:
            if isinstance(self.type, (InputTypes, OutputTypes)):  # wipp
                value = WIPP_TYPES[self.type](value)
            else:
                value = WIPP_TYPES[self.type.value](
                    value,
                )  # compute, type does not inherit from str

            if isinstance(value, pathlib.Path):
                value = value.absolute()
                if self._fs:
                    assert self._fs.exists(
                        str(value),
                    ), f"{value} is invalid or does not exist"
                    assert self._fs.isdir(
                        str(value),
                    ), f"{value} is not a valid directory"
                else:
                    assert value.exists(), f"{value} is invalid or does not exist"
                    assert value.is_dir(), f"{value} is not a valid directory"

        super().__setattr__("value", value)

    def __setattr__(self, name: str, value: Any) -> None:  # ruff: noqa: ANN401
        """Set I/O attributes."""
        if name not in ["value", "id", "_fs"]:
            # Don't permit any other values to be changed
            msg = f"Cannot set property: {name}"
            raise TypeError(msg)

        super().__setattr__(name, value)

        if name == "value":
            self._validate()


class Output(IOBase):  # pylint: disable=R0903
    """Required until JSON schema is fixed."""

    if PYDANTIC_V2:
        name: Annotated[
            str,
            StringConstraints(pattern=r"^[a-zA-Z0-9][-a-zA-Z0-9]*$"),
        ] = Field(
            ...,
            examples=["outputCollection"],
            title="Output name",
        )
        description: Annotated[str, StringConstraints(pattern=r"^(.*)$")] = Field(
            ...,
            examples=["Output collection"],
            title="Output description",
        )
    else:
        name: constr(regex=r"^[a-zA-Z0-9][-a-zA-Z0-9]*$") = Field(
            ...,
            examples=["outputCollection"],
            title="Output name",
        )
        description: constr(regex=r"^(.*)$") = Field(
            ...,
            examples=["Output collection"],
            title="Output description",
        )
    type: OutputTypes = Field(
        ...,
        examples=["stitchingVector", "collection"],
        title="Output type",
    )


class Input(IOBase):  # pylint: disable=R0903
    """Required until JSON schema is fixed."""

    if PYDANTIC_V2:
        name: Annotated[
            str,
            StringConstraints(pattern=r"^[a-zA-Z0-9][-a-zA-Z0-9]*$"),
        ] = Field(
            ...,
            description="Input name as expected by the plugin CLI",
            examples=["inputImages", "fileNamePattern", "thresholdValue"],
            title="Input name",
        )
        description: Annotated[str, StringConstraints(pattern=r"^(.*)$")] = Field(
            ...,
            examples=["Input Images"],
            title="Input description",
        )
    else:
        name: constr(regex=r"^[a-zA-Z0-9][-a-zA-Z0-9]*$") = Field(
            ...,
            description="Input name as expected by the plugin CLI",
            examples=["inputImages", "fileNamePattern", "thresholdValue"],
            title="Input name",
        )
        description: constr(regex=r"^(.*)$") = Field(
            ...,
            examples=["Input Images"],
            title="Input description",
        )
    type: InputTypes
    required: Optional[bool] = Field(
        True,
        description="Whether an input is required or not",
        examples=[True],
        title="Required input",
    )

    def __init__(self, **data) -> None:  # ruff: noqa: ANN003
        """Initialize input."""
        super().__init__(**data)

        if self.description is None:
            logger.warning(
                f"""
                The input ({self.name}) is missing the description field.
                This field is not required but should be filled in.
                """,
            )


def _check_version_number(value: Union[str, int]) -> bool:
    if isinstance(value, int):
        value = str(value)
    if "-" in value:
        value = value.split("-")[0]
    if len(value) > 1 and value[0] == "0":
        return False
    return bool(re.match(r"^\d+$", value))


SEMVER_REGEX = re.compile(
    "^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\."
    "(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]"
    "\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*"
    "[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>"
    "[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

if PYDANTIC_V2:

    def semver_validator(ver: str) -> str:
        """Validate a version against semver regex.

        This validator is used by Pydantic in the `Version` object.
        """
        re_match = SEMVER_REGEX.match(ver)
        if not re_match:
            raise ValueError(
                f"invalid version ({ver}). Version must follow semantic versioning (see semver.org)"
            )
        return ver

    SemVerRoot = Annotated[str, AfterValidator(semver_validator)]

    @dataclass
    class Version:
        """SemVer object."""

        _root: SemVerRoot
        major: int = Field(..., init=False)
        minor: int = Field(..., init=False)
        patch: int = Field(..., init=False)
        prerelease: str = Field(..., init=False)
        buildmetadata: str = Field(..., init=False)

        def __post_init__(self) -> None:
            re_match = SEMVER_REGEX.match(self._root)
            match_dict = re_match.groupdict()
            self.major = int(match_dict["major"])
            self.minor = int(match_dict["minor"])
            self.patch = int(match_dict["patch"])
            self.prerelease = match_dict["prerelease"]
            self.buildmetadata = match_dict["buildmetadata"]

        def __str__(self) -> str:
            """Return string representation of Version object."""
            return self._root

        @singledispatchmethod
        def __lt__(self, other: Any) -> bool:
            """Compare if Version is less than other object."""
            msg = "invalid type for comparison."
            raise TypeError(msg)

        @singledispatchmethod
        def __gt__(self, other: Any) -> bool:
            """Compare if Version is less than other object."""
            msg = "invalid type for comparison."
            raise TypeError(msg)

        @singledispatchmethod
        def __eq__(self, other: Any) -> bool:
            """Compare if two Version objects are equal."""
            msg = "invalid type for comparison."
            raise TypeError(msg)

        def __hash__(self) -> int:
            """Needed to use Version objects as dict keys."""
            return hash(self._root)

        def __repr__(self) -> str:
            """Return string representation of Version object."""
            return self._root

    @Version.__eq__.register(str)  # pylint: disable=no-member
    def _(self, other):
        return self == Version(other)

    @Version.__lt__.register(str)  # pylint: disable=no-member
    def _(self, other):
        return self < Version(other)

    @Version.__gt__.register(str)  # pylint: disable=no-member
    def _(self, other):
        return self > Version(other)

else:  # PYDANTIC_V1

    class Version(BaseModel):
        """SemVer object."""

        version: str

        def __init__(self, version: str) -> None:
            """Initialize Version object."""
            super().__init__(version=version)

        @validator("version")
        def semantic_version(
            cls,
            value,
        ):  # ruff: noqa: ANN202, N805, ANN001
            """Pydantic Validator to check semver."""
            assert bool(
                SEMVER_REGEX.match(value),
            ), f"""Invalid version ({value}).
            Version must follow semantic versioning (see semver.org)"""

            return value

        @property
        def major(self):
            """Return x from x.y.z ."""
            return int(self.version.split(".")[0])

        @property
        def minor(self):
            """Return y from x.y.z ."""
            return int(self.version.split(".")[1])

        @property
        def patch(self):
            """Return z from x.y.z ."""
            return int(self.version.split(".")[2])

        @property
        def prerelease(self):
            """Return q from x.y.z.q ."""
            match = SEMVER_REGEX.match(self.version)
            return match.group("prerelease")

        @property
        def buildmetadata(self):
            """Return q from x.y.z.q ."""
            match = SEMVER_REGEX.match(self.version)
            return match.group("buildmetadata")

        def __str__(self) -> str:
            """Return string representation of Version object."""
            return self.version

        @singledispatchmethod
        def __lt__(self, other: Any) -> bool:
            """Compare if Version is less than other object."""
            msg = "invalid type for comparison."
            raise TypeError(msg)

        @singledispatchmethod
        def __gt__(self, other: Any) -> bool:
            """Compare if Version is less than other object."""
            msg = "invalid type for comparison."
            raise TypeError(msg)

        @singledispatchmethod
        def __eq__(self, other: Any) -> bool:
            """Compare if two Version objects are equal."""
            msg = "invalid type for comparison."
            raise TypeError(msg)

        def __hash__(self) -> int:
            """Needed to use Version objects as dict keys."""
            return hash(self.version)

    @Version.__eq__.register(str)  # pylint: disable=no-member
    def _(self, other):
        return self == Version(**{"version": other})

    @Version.__lt__.register(str)  # pylint: disable=no-member
    def _(self, other):
        v = Version(**{"version": other})
        return self < v

    @Version.__gt__.register(str)  # pylint: disable=no-member
    def _(self, other):
        v = Version(**{"version": other})
        return self > v


@Version.__eq__.register(Version)  # pylint: disable=no-member
def _(self, other):
    return (
        other.major == self.major
        and other.minor == self.minor
        and other.patch == self.patch
        and other.prerelease == self.prerelease
        and other.buildmetadata == self.buildmetadata
    )


def prerelease_lt(pre1: str, pre2: str) -> bool:  # pylint: disable=R0911
    """Check for precedence in prerelease versions.

    Follows the algorithm defined in [semver.org](https://semver.org/#spec-item-11)
    """
    set_1 = pre1.split(".")
    set_2 = pre2.split(".")
    zipped = zip_longest(set_1, set_2)  # zip with `None` as default
    for pair in zipped:
        if pair[0] == pair[1]:
            continue
        is_digit_one = pair[0].isdigit() if pair[0] is not None else False
        is_digit_two = pair[1].isdigit() if pair[1] is not None else False
        if is_digit_one and is_digit_two:
            if int(pair[0]) < int(pair[1]):
                return True
            return False  # pair[0] > pair[1]
        if pair[0] is not None and pair[1] is None:  # pre1 is longer, allelseequal
            return False
        if is_digit_one and not is_digit_two and pair[1] is not None:
            # numeric identifiers always have lower precedence
            # than non-numeric identifiers
            return True
        if is_digit_two and not is_digit_one and pair[0] is not None:
            return False
        if pair[0] is None and pair[1] is not None:  # pre2 is longer, allelseequal
            return True
        if pair[0] < pair[1]:
            return True
        return False  # pair[0] > pair[1]
    return False


# Example: 1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta
# < 1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0.


@Version.__lt__.register(Version)  # pylint: disable=no-member
def _(self, other):
    if self.major < other.major:  # X.y.z // P.q.r | X < P
        return True
    if self.major == other.major:  # x.Y.z // x.Q.r
        if self.minor < other.minor:  # | Y < Q
            # if other.minor > self.minor:
            return True
        if self.minor == other.minor:  # x.y.Z // x.y.R
            # if other.patch > self.patch:
            if self.patch < other.patch:  # | Z < R
                return True
            if self.patch == other.patch:  # x.y.z // x.y.z
                if self.prerelease is not None:
                    if other.prerelease is None:
                        return True
                    # other.prerelease is not None
                    return prerelease_lt(self.prerelease, other.prerelease)
            return False
        return False
    return False


@Version.__gt__.register(Version)  # pylint: disable=no-member
def _(self, other):
    return other < self


class DuplicateVersionFoundError(Exception):
    """Raise when two equal versions found."""


CWL_INPUT_TYPES = {
    "path": "Directory",  # always Dir? Yes
    "string": "string",
    "number": "double",
    "boolean": "boolean",
    "genericData": "Directory",
    "collection": "Directory",
    "enum": "string",  # for compatibility with workflows
    "stitchingVector": "Directory",
    # not yet implemented: array
}


def _type_in(inp: Input):
    """Return appropriate value for `type` based on input type."""
    val = inp.type.value
    req = "" if inp.required else "?"

    # NOT compatible with CWL workflows, ok in CLT
    # if val == "enum":
    #     if input.required:

    # if val in CWL_INPUT_TYPES:
    return CWL_INPUT_TYPES[val] + req if val in CWL_INPUT_TYPES else "string" + req


def input_to_cwl(inp: Input):
    """Return dict of inputs for cwl."""
    return {
        f"{inp.name}": {
            "type": _type_in(inp),
            "inputBinding": {"prefix": f"--{inp.name}"},
        },
    }


def output_to_cwl(out: Output):
    """Return dict of output args for cwl for input section."""
    return {
        f"{out.name}": {
            "type": "Directory",
            "inputBinding": {"prefix": f"--{out.name}"},
        },
    }


def outputs_cwl(out: Output):
    """Return dict of output for `outputs` in cwl."""
    return {
        f"{out.name}": {
            "type": "Directory",
            "outputBinding": {"glob": f"$(inputs.{out.name}.basename)"},
        },
    }


# -- I/O as arguments in .yml


@singledispatch
def _io_value_to_yml(io) -> Union[str, dict]:
    return str(io)


@_io_value_to_yml.register
def _(io: pathlib.Path):
    return {"class": "Directory", "location": str(io)}


@_io_value_to_yml.register
def _(io: enum.Enum):
    return io.name


def io_to_yml(io):
    """Return IO entry for yml file."""
    return _io_value_to_yml(io.value)
