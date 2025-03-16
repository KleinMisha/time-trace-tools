from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from time_trace import TimeTrace


@dataclass
class MockTimeTrace(TimeTrace):
    value_one: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    value_two: NDArray[np.float64] = field(default_factory=lambda: np.array([]))

    @property
    def _values(
        self,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        return all the value arrays as a tuple.
        See subclasses for specific implementation
        """
        return (self.value_one, self.value_two)

    @property
    def _value_names(self) -> tuple[str, ...]:
        """
        return a tuple of the names of the values. Should be same as the variable names
        used to instantiate class instance.
        """
        return ("value_one", "value_two")
