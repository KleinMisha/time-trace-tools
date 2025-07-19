"""
Test BaseTransformation
"""

from copy import deepcopy

import numpy as np
import pytest

from tests.data_processing.mock_transformation import MockTransformation
from tests.data_types.mock_time_trace import MockTimeTrace

NUMBER_OF_TRACES = 10


@pytest.fixture
def mock_trace_list() -> list[MockTimeTrace]:
    t = np.linspace(0, 100, 10)
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    return [
        MockTimeTrace(ID=f"trace_{n}", t=t, value_one=x, value_two=y)
        for n in range(NUMBER_OF_TRACES)
    ]


@pytest.fixture
def target_traces() -> list[str]:
    return [f"trace_{n}" for n in range(NUMBER_OF_TRACES) if n % 2 == 0]


def test_apply_transform_to_target_traces(
    mock_trace_list: list[MockTimeTrace], target_traces: list[str]
) -> None:
    """check that Transformation is only applied to the target traces, not to the others"""
    mock_transformation = MockTransformation(target_traces)
    new_traces = mock_transformation.apply(mock_trace_list)
    for trace in new_traces:
        if trace.ID in target_traces:
            assert trace.__getattribute__("applied")


def test_apply_transform_not_on_other_traces(
    mock_trace_list: list[MockTimeTrace], target_traces: list[str]
) -> None:
    """check that Transformation is only applied to the target traces, not to the others"""
    mock_transformation = MockTransformation(target_traces)
    new_traces = mock_transformation.apply(mock_trace_list)
    for trace in new_traces:
        if trace.ID not in target_traces:
            assert not hasattr(trace, "applied")


def test_do_not_modify_original_traces(
    mock_trace_list: list[MockTimeTrace], target_traces: list[str]
) -> None:
    """validate that original traces are not modified"""
    mock_transformation = MockTransformation(target_traces)
    current_traces = deepcopy(mock_trace_list)
    _ = mock_transformation.apply(current_traces)
    for trace in mock_trace_list:
        assert not hasattr(trace, "applied")
