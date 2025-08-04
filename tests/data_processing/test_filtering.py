"""
Test the common logic implemented in the Filter class
"""

import numpy as np
import pytest
from numpy.typing import NDArray

from time_trace_tools.data_processing.filtering import Filter
from time_trace_tools.data_processing.processor import ExperimentProcessor
from tests.data_types.mock_experiment import (
    MockExperiment,
    create_mock_dataset,
    parse_mock_dataset,
)

NUMBER_MOCK_TRACES = 100


@pytest.fixture
def experiment(number_of_traces: int = NUMBER_MOCK_TRACES) -> MockExperiment:
    """
    generate a mock Experiment
    """
    exp = MockExperiment(ID="mock")
    data = create_mock_dataset(number_traces=number_of_traces)
    one, two, time = parse_mock_dataset(data)
    exp._raw_data = one, two, time
    exp.create_traces_from_raw_data()
    return exp


class MockFilter(Filter):
    """Dummy filter operation that turns the entire signal into 42's"""

    def filter(
        self, time: NDArray[np.floating], raw_signal: NDArray[np.floating]
    ) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
        """all values become 42"""
        filtered_signal = np.array([42.0] * len(raw_signal))
        return time, filtered_signal


def test_only_filter_target_coordinate(experiment: MockExperiment) -> None:
    """Verify logic will only be applied to the existing coordinate"""
    first_half_of_traces = [f"trace_{i}" for i in range(NUMBER_MOCK_TRACES // 2)]
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(
        MockFilter(
            target_traces=first_half_of_traces,
            coordinate="value_one",
        )
    )
    processor.run()

    modified_experiment = processor.get_current_experiment()
    for trace in modified_experiment.traces:
        if trace.ID in first_half_of_traces:
            # the modified coordinate:
            assert all(value == 42.0 for value in trace.value_one)
            # unmodified coordinates:
            assert all(value == 1.0 for value in trace.value_two)


def test_validate_coordinate(experiment: MockExperiment) -> None:
    """Verify an error is raised when attempting to access a non-existing value array"""
    first_half_of_traces = [f"trace_{i}" for i in range(NUMBER_MOCK_TRACES // 2)]
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(
        MockFilter(
            target_traces=first_half_of_traces,
            coordinate="value_three",
        )
    )
    with pytest.raises(
        AttributeError,
        match="Trace trace_1 does not have a value-array named value_three",
    ):
        processor.run()


def test_only_filter_target_traces(experiment: MockExperiment) -> None:
    """Traces not in the target_traces list should just get passed onwards without modification"""
    first_half_of_traces = [f"trace_{i}" for i in range(NUMBER_MOCK_TRACES // 2)]
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(
        MockFilter(
            target_traces=first_half_of_traces,
            coordinate="value_one",
        )
    )
    processor.run()

    modified_experiment = processor.get_current_experiment()
    for trace in modified_experiment.traces:
        if trace.ID not in first_half_of_traces:
            assert all(value == 1.0 for value in trace.value_one)
            assert all(value == 1.0 for value in trace.value_one)
