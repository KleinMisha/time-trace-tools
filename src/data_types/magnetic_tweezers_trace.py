"""
Implementation of a TimeTrace suitable for typical magnetic tweezers (MT) experiments.
These are time traces with x,y, and z position information of the bead.
"""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from time_trace import TimeTrace


@dataclass
class MagneticTweezersTrace(TimeTrace):
    # A slight bit disappointing I cannot just define a new variable here without default value
    # At least this seems like a small compromise to make, user-experience wise.
    # i.e. Always call it as MagneticTweezersTrace(ID,t , x=..., y=..., z=...)
    x: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    y: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    z: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    is_REF: bool = False

    @property
    def _values(
        self,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
        """
        return all the value arrays as a tuple.
        See subclasses for specific implementation
        """
        return (self.x, self.y, self.z)

    @property
    def _value_names(self) -> tuple[str, ...]:
        """
        return a tuple of the names of the values. Should be same as the variable names
        used to instantiate class instance.
        """
        return ("x", "y", "z")
