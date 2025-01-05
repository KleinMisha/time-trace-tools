"""
Implementation of a TimeTrace suitable for typical magnetic tweezers (MT) experiments.
These are time traces with x,y, and z position information of the bead.
"""

from dataclasses import dataclass, field

import numpy as np
from time_trace import TimeTrace


@dataclass
class MagneticTweezersTrace(TimeTrace):
    # A slight bit disappointing I cannot just define a new variable here without default value
    # At least this seems like a small compromise to make, user-experience wise.
    # i.e. Always call it as MagneticTweezersTrace(ID,t , x=..., y=..., z=...)
    x: np.ndarray = field(default_factory=lambda: np.array([]))
    y: np.ndarray = field(default_factory=lambda: np.array([]))
    z: np.ndarray = field(default_factory=lambda: np.array([]))

    @property
    def _values(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        return all the value arrays as a tuple.
        See subclasses for specific implementation
        """
        return (self.x, self.y, self.z)
