"""
Test data_processing.filtering.MovingAverageFilter

NOTE: The Filter is already tested in the context of ExperimentProcessor. Hence, only need to test specific filter logic here
"""

from itertools import product

import numpy as np
import pytest

from time_trace_tools.data_processing.filtering import MovingAverageFiler


@pytest.mark.parametrize(
    ("time_window, acquisition_frequency"),
    list(product([1.0, 5.0, 10.0], [1.0, 10.0])),
)
def test_window_size_determination(
    time_window: float, acquisition_frequency: float
) -> None:
    """
    simple check if the window size is as desired
    """
    moving_average = MovingAverageFiler(
        target_traces=[""],
        coordinate="",
        time_window=time_window,
        acquisition_frequency=acquisition_frequency,
    )

    assert moving_average._window_size == int(time_window * acquisition_frequency)


@pytest.mark.parametrize(
    "time_window, acquisition_frequency, raw_signal, expected_signal",
    [  # If window size equals 1, then you should get back the input signal
        (10.0, 1.0, 42.0 * np.ones(100), 42.0 * np.ones(100)),
        # if signal is all 1.0's , filtered signal remains that as well
        (10.0, 1.0, np.ones(100), np.ones(100)),
        # simple filter averaging neighboring points
        (1.0, 2.0, [n for n in range(1, 100)], [1.0] + [n + 0.5 for n in range(1, 99)]),
        # turning around time window and acquisition frequency should result in the same
        (2.0, 1.0, [n for n in range(1, 100)], [1.0] + [n + 0.5 for n in range(1, 99)]),
        # window of 3 points
        (
            3.0,
            1.0,
            [n for n in range(1, 100)],
            [1.0, 1.5] + [float(n - 1) for n in range(3, 100)],
        ),
    ],
)
def test_moving_average(
    time_window: float,
    acquisition_frequency: float,
    raw_signal: np.ndarray,
    expected_signal: np.ndarray,
) -> None:
    """Check filter returns the expected signal for some known test cases"""

    time_array = np.array([1.0 / acquisition_frequency] * len(raw_signal))
    moving_average = MovingAverageFiler(
        target_traces=[""],
        coordinate="",
        time_window=time_window,
        acquisition_frequency=acquisition_frequency,
    )
    _, filtered_signal = moving_average.filter(
        time_array, raw_signal=np.array(raw_signal)
    )

    assert np.array_equal(filtered_signal, np.array(expected_signal)), print(
        filtered_signal, expected_signal
    )
