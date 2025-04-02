"""
Mock experiment that represents a set of mock time traces
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from src.data_types.experiment import Experiment
from tests.data_types.mock_time_trace import MockTimeTrace


def create_mock_dataset(number_traces: int = 100) -> NDArray[np.floating]:
    """
    generate a table containing a mock dataset

    format:
    time | value_one_1 | value_two_1 | value_one_2 | value_two_2 | .... | value_one_N | value_two_N
    """

    # generate a set of MockTimeTrace instances
    t = np.linspace(0, 100, 10)
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    mock_traces = [
        MockTimeTrace(ID="mock", t=t, value_one=x, value_two=y)
        for _ in range(number_traces)
    ]

    # generate the table with data values
    data_table = [t]
    for trace in mock_traces:
        data_table.append(trace.value_one)
        data_table.append(trace.value_two)

    return np.array(data_table).T


def parse_mock_dataset(
    data_table: NDArray[np.floating],
) -> tuple[NDArray[np.floating], NDArray[np.floating], NDArray[np.floating]]:
    """
    parse the mock datafile created in function above
    """
    time = data_table[:, 0]  # First column (time vector)
    value_columns = data_table[:, 1:]  # Remaining columns

    One = value_columns[:, ::2]  # Take every even-indexed column (x-values)
    Two = value_columns[:, 1::2]  # Take every odd-indexed column (y-values)
    return One, Two, time


@dataclass
class MockExperiment(Experiment[MockTimeTrace]):
    """
    Mock Experiment with traces that are of type MockTimeTrace
    """

    def _create_trace_list_from_raw_data(self) -> list[MockTimeTrace]:
        """
        Implement how the traces should be instantiated based on the loaded raw data
        As data from different experiments might have different structures, intentionally left this as abstract method
        """
        One, Two, time = self._raw_data
        trace_list = []
        for index, (one, two) in enumerate(zip(One.T, Two.T)):
            trace_list.append(
                MockTimeTrace(
                    ID=f"trace_{index + 1}", t=time, value_one=one, value_two=two
                )
            )
        return trace_list
