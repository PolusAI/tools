"""WIPP Hardware Requirements Functions."""

# import polus.plugins as pp
from ict.hardware import CPU, GPU, HardwareRequirements, Memory

from polus.tools.plugins._plugins.models.wipp import (
    ResourceRequirements as WIPPResourceRequirements,
)


def convert_wipp_hardware_to_ict(
    wipp: WIPPResourceRequirements,
) -> HardwareRequirements:
    """Convert WIPP ResourceRequirements to ICT HardwareRequirements."""
    cpu_ = CPU(
        min=wipp.coresMin,
        recommended=None,
        type=None,
    )
    memory_ = Memory(
        min=str(wipp.ramMin) + "Mi" if wipp.ramMin else None,
        recommended=None,
    )
    gpu_ = GPU(
        enabled=None,
        required=wipp.gpu,
        type=None,
    )
    return HardwareRequirements(
        cpu=cpu_,
        memory=memory_,
        gpu=gpu_,
    )
