"""
test things specific to the implementation of MagneticTweezersTrace
NOTE: This is me learning how to work with pytest. Partially writing these unit tests to increase the coverage / see how this coverage report works etc.
the tests written here are trivial of course.
"""

import numpy as np
import pytest

from src.data_types.magnetic_tweezers_trace import MagneticTweezersTrace


@pytest.fixture
def mt_trace() -> MagneticTweezersTrace:
    """
    generate a mock MagneticTweezersTrace
    NOTE: Shouldn't use random numbers in a unittest, but given there is no way any of these tests can fail for any possible outcome, I think it is still fine.
    TODO: Avoid using random numbers?
    """
    t = np.linspace(0, 100, 10, dtype=np.float64)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))
    return MagneticTweezersTrace(ID="mock", t=t, x=x, y=y, z=z)


def test_value_names(mt_trace: MagneticTweezersTrace) -> None:
    assert mt_trace._value_names == ("x", "y", "z")


def test_values(mt_trace: MagneticTweezersTrace) -> None:
    assert mt_trace._values == (mt_trace.x, mt_trace.y, mt_trace.z)
