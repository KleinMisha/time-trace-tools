"""
unit tests for trace_operations.py

NOTE: addition, multiplication, subtraction are tested directly in the test_trace.py file as it checks if overloading of __add__(), __min__(), etc. works properly
"""

import numpy as np
import pytest
from exception_definitions import InvalidTimeTraceError
from magnetic_tweezers_trace import MagneticTweezersTrace
from mock_time_trace import MockTimeTrace
from trace_operations import add, average_traces

Scalar = int | float | np.integer | np.floating


@pytest.fixture
def time_trace() -> MockTimeTrace:
    """
    generate a mock (MagneticTweezers)TimeTrace
    """
    t = np.linspace(0, 100, 10, dtype=np.float64)
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    return MockTimeTrace(ID="mock", t=t, value_one=x, value_two=y)


@pytest.fixture
def shorter_time_trace() -> MockTimeTrace:
    t = np.linspace(0, 100, 20, dtype=np.float64)
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    return MockTimeTrace(ID="mock", t=t, value_one=x, value_two=y)


@pytest.fixture
def shifted_time_trace() -> MockTimeTrace:
    t = np.linspace(0, 100, 10, dtype=np.float64) + 5.0
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    return MockTimeTrace(ID="mock", t=t, value_one=x, value_two=y)


@pytest.fixture
def mt_trace() -> MagneticTweezersTrace:
    t = np.linspace(0, 100, 10, dtype=np.float64)
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    z = np.array([1.0] * len(t))
    return MagneticTweezersTrace(ID="mock", t=t, x=x, y=y, z=z)


@pytest.fixture
def scalar() -> Scalar:
    """
    to avoid typing this hard-coded value multiple times (in case there will be more functions to test later on)
    """
    return 10.0


def test_averaging(time_trace: MockTimeTrace, scalar: Scalar) -> None:
    """
    test calculating the average of
    - trace_1
    - trace_1 * scalar

    result should always be (1 + scalar)/2 * original value
    """
    first_trace = time_trace
    second_trace = time_trace * scalar
    new_trace = average_traces(trace_list=[first_trace, second_trace])
    for new_values, original_values in zip(new_trace._values, time_trace._values):
        assert np.all(new_values == (1.0 + scalar) / 2 * original_values)


def test_invalid_addition_unequal_length(
    time_trace: MockTimeTrace, shorter_time_trace: MockTimeTrace
) -> None:
    with pytest.raises(InvalidTimeTraceError):
        add(time_trace, shorter_time_trace)


def test_invalid_addition_shifted_traces(
    time_trace: MockTimeTrace, shifted_time_trace: MockTimeTrace
) -> None:
    with pytest.raises(InvalidTimeTraceError):
        add(time_trace, shifted_time_trace)


def test_incompatible_trace_types(
    time_trace: MockTimeTrace, mt_trace: MagneticTweezersTrace
) -> None:
    with pytest.raises(InvalidTimeTraceError):
        add(time_trace, mt_trace)
