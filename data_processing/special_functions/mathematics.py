"""
Commonly used functions / general mathematics
"""

import numpy as np


def gaussian():
    """
    Gaussian function
    """
    pass


def exponential():
    """
    simple exponential decay + offset
    """
    pass


def line(x: np.ndarray, slope: float, offset: float) -> np.ndarray:
    """
    A line
    """
    a = slope
    b = offset
    return a * x + b
