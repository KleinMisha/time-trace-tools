"""
!: MOVE TO DIFFERENT REPOSITORY !!!!
"""

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from src.data_processing.transformation import Transformation
from src.data_types.time_trace import TimeTrace


@dataclass(eq=False)
class NucleotidePositionTrace(TimeTrace):
    """
    TimeTrace type to represent a signal of "nucleotide position VS time". Typically a single value is needed to keep track of
    """

    nucleotide_position: NDArray[np.floating] = field(
        default_factory=lambda: np.array([])
    )

    @property
    def _values(self) -> tuple[NDArray[np.floating]]:
        return (self.nucleotide_position,)

    @property
    def _value_names(self) -> tuple[str]:
        return ("nucleotide_position",)


@dataclass
class NucleotideConversion(Transformation):
    """
    specific to primer-extension experiments
    convert bead height (magnetic tweezers) to the position of the polymerase along the substrate
    """

    nucleic_acid: Literal["RNA", "DNA"]
    direction: Literal["ss_to_ds", "ds_to_ss"]

    def apply(self, trace_list: list[TimeTrace]) -> list[TimeTrace]:
        return NotImplemented
