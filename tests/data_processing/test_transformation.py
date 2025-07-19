"""
Test BaseTransformation
"""

from copy import deepcopy

import numpy as np
import pytest

from tests.data_processing.mock_transformation import (
    MockCoordinateTransformation,
    MockTransformation,
)
from tests.data_types.mock_time_trace import MockTimeTrace

NUMBER_OF_TRACES = 10


@pytest.fixture
def mock_trace_list() -> list[MockTimeTrace]:
    t = np.linspace(0, 100, 10)
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    return [
        MockTimeTrace(ID=f"trace_{n + 1}", t=t, value_one=x, value_two=y)
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


def test_apply_to_all_traces(mock_trace_list: list[MockTimeTrace]) -> None:
    """Test that when BaseTransformation is given an empty list of targets (or None) it will apply the transformation to all traces"""
    mock_transformation = MockTransformation(None)
    new_traces = mock_transformation.apply(mock_trace_list)
    for trace in new_traces:
        assert trace.__getattribute__("applied")


def test_modify_valid_coordinate_array(mock_trace_list: list[MockTimeTrace]) -> None:
    """Test you only modified 'value one'"""
    mock_transformation = MockCoordinateTransformation("value_one", None)
    new_traces = mock_transformation.apply(mock_trace_list)
    for trace in new_traces:
        # the modified coordinate:
        assert all(value == 42.0 for value in trace.value_one)
        # unmodified coordinates:
        assert all(value == 1.0 for value in trace.value_two)


def test_invalid_coordinate_name(mock_trace_list: list[MockTimeTrace]) -> None:
    """Check validation indeed raises exception trying to apply transformation to non-existing coordinate"""
    mock_transformation = MockCoordinateTransformation("NOT_EXISTING", None)
    with pytest.raises(
        AttributeError,
        match="Trace trace_1 does not have a value-array named NOT_EXISTING",
    ):
        mock_transformation.apply(mock_trace_list)
