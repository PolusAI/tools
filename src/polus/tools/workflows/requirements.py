"""CWL Requirements."""

from typing import Any
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from polus.tools.workflows.types import Expression


class ProcessRequirement(BaseModel):
    """Base class for all process requirements."""

    model_config = ConfigDict(populate_by_name=True)

    class_: str = Field(..., alias="class")


class SubworkflowFeatureRequirement(ProcessRequirement):
    """Needed if a Workflow references other Workflows."""

    class_: str = "SubworkflowFeatureRequirement"


class SoftwarePackages(BaseModel):
    """SoftwarePackages."""

    package: str
    version: Optional[list[str]]
    specs: Optional[list[str]]


class SoftwareRequirement(ProcessRequirement):
    """Software requirements."""

    class_: str = "SoftwareRequirement"
    packages: list[SoftwarePackages]


class DockerRequirement(ProcessRequirement):
    """Docker requirements."""

    model_config = ConfigDict(populate_by_name=True)

    class_: str = "DockerRequirement"
    docker_pull: Optional[str] = Field(None, alias="dockerPull")
    docker_load: Optional[str] = Field(None, alias="dockerLoad")
    docker_file: Optional[str] = Field(None, alias="dockerFile")
    docker_import: Optional[str] = Field(None, alias="dockerImport")
    docker_image_id: Optional[str] = Field(None, alias="dockerImageId")
    docker_output_directory: Optional[str] = Field(None, alias="dockerOutputDirectory")


class ScatterFeatureRequirement(ProcessRequirement):
    """ScatterFeatureRequirement."""

    class_: str = "ScatterFeatureRequirement"


class InlineJavascriptRequirement(ProcessRequirement):
    """InlineJavascriptRequirement."""

    model_config = ConfigDict(populate_by_name=True)

    class_: str = "InlineJavascriptRequirement"
    expression_lib: Optional[list[str]] = Field(None, alias="expressionLib")


class InitialWorkDirRequirement(ProcessRequirement):
    """InitialWorkDirRequirement."""

    class_: str = "InitialWorkDirRequirement"
    listing: list[Any]  # : ANN401


class EnvironmentDef(BaseModel):
    """EnvironmentDef."""

    env_name: str = Field(None, alias="envName")
    env_value: Union[str, Expression] = Field(None, alias="envValue")


class EnvVarRequirement(ProcessRequirement):
    """EnvVarRequirement."""

    model_config = ConfigDict(populate_by_name=True)

    class_: str = "EnvVarRequirement"
    env_def: list[EnvironmentDef] = Field([], alias="envDef")


class ResourceRequirement(ProcessRequirement):
    """ResourceRequirement."""

    model_config = ConfigDict(populate_by_name=True)

    class_: str = "ResourceRequirement"
    cores_min: Optional[Union[int, float]] = Field(1, alias="coresMin")
    cores_max: Optional[Union[int, float]] = Field(None, alias="coresMax")
    ram_min: Optional[Union[int, float]] = Field(256, alias="ramMin")
    ram_max: Optional[Union[int, float]] = Field(None, alias="ramMax")
    tmpdir_min: Optional[Union[int, float]] = Field(None, alias="tmpdirMin")
    tmpdir_max: Optional[Union[int, float]] = Field(None, alias="tmpdirMax")
    outdir_min: Optional[Union[int, float]] = Field(None, alias="outdirMin")
    outdir_max: Optional[Union[int, float]] = Field(None, alias="outdirMax")


class SchemaDefRequirement(BaseModel):
    """SchemaDefRequirement.

    https://www.commonwl.org/v1.2/Workflow.html#SchemaDefRequirement
    """

    pass


class NetworkAccess(ProcessRequirement):
    """NetworkAccess.

    https://www.commonwl.org/v1.2/CommandLineTool.html#NetworkAccess.
    """

    model_config = ConfigDict(populate_by_name=True)

    class_: str = "NetworkAccess"
    network_access: Union[bool, Expression] = Field(True, alias="networkAccess")
