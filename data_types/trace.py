"""
Core class to define a single (time-) trace
(In principle not restricted to data VS time and could be force VS extention etc.)
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Union


@dataclass
class Trace:
    """
    A individual time-trace
    """

    x: Union[List[float], np.ndarray]
    y: Union[List[float], np.ndarray]
    z: Union[List[float], np.ndarray]
    t: Union[List[float], np.ndarray]
    id: str
    is_REF_bead: bool
