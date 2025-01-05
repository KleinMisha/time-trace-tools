"""
basic operations that allow us to add, subtract, etc. multiple traces.
Also includes shifting a trace to the left/right
"""

import numpy as np
from time_trace import TimeTrace


def add(trace_1: TimeTrace, trace_2: TimeTrace) -> TimeTrace:
    """
    add all values together
    """
    raise NotImplementedError


def add_constant_value(trace: TimeTrace, value: float) -> TimeTrace:
    """
    add/subtract constant value from all channels
    """
    raise NotImplementedError


def average_trace(trace_list: list[TimeTrace]) -> TimeTrace:
    raise NotImplementedError


def multiply_by_value(trace: TimeTrace, value: float) -> TimeTrace:
    raise NotImplementedError
