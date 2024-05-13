"""Extending automatically generated compute model.

This file modifies and extend certain fields and
functions of PolusComputeSchema.py which is automatically
generated by datamodel-codegen from JSON schema.
"""

from polus.tools.plugins._plugins.io import IOBase, Version
from polus.tools.plugins._plugins.models.pydanticv1.PolusComputeSchema import (
    PluginInput,
    PluginOutput,
    PluginSchema,
)


class PluginInput(PluginInput, IOBase):  # type: ignore
    """Base Class for Input Args."""


class PluginOutput(PluginOutput, IOBase):  # type: ignore
    """Base Class for Output Args."""


class PluginSchema(PluginSchema):  # type: ignore
    """Extended Compute Plugin Schema with extended IO defs."""

    inputs: list[PluginInput]
    outputs: list[PluginOutput]
    version: Version
