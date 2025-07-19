"""
Common filter Transformations

-- Misha, June 2025
"""

from abc import abstractmethod
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.signal import filtfilt, firwin, kaiserord

from src.data_processing.transformation import CoordinateTransformation
from src.data_types.type_definitions import TimeTraceType


@dataclass
class Filter(CoordinateTransformation):
    """A generic Filter Transformation. Gather common functionality in here to avoid duplicate code/ allow for simple testing."""

    @abstractmethod
    def filter(
        self, time: NDArray[np.floating], raw_signal: NDArray[np.floating]
    ) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
        """Implement the specific filtering operation here. Return (time, filtered_signal)"""

    def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
        """creation of the filtered TimeTrace has shared logic independent of the actual filter operation"""
        self.target_traces
        time = trace.t
        value_array = trace.__getattribute__(self.coordinate)
        filtered_time, filtered_values = self.filter(time, value_array)
        filtered_trace = trace
        filtered_trace.__setattr__("t", filtered_time)
        filtered_trace.__setattr__(self.coordinate, filtered_values)
        return filtered_trace


@dataclass
class KaiserBesselFilter(Filter):
    """
    Kaiser-Bessel (low-pass) filter.
    ---
    Typical filter used for polymerase primer-extension traces.
    """

    acquisition_frequency: float = 58.0
    cutoff_frequency: float = 2.0
    transition_width: float = 0.01  # relative to nyquist frequency. So width in Hz = width * acquisition_frequency /2
    stopband_attenuation_dB: float = 100

    def filter(
        self, time: NDArray[np.floating], raw_signal: NDArray[np.floating]
    ) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
        """apply the Kaiser-Bessel filter to a single time trace. "signal" is the value array named self.coordinate."""
        # Create Finite Impulse Response (FIR) filter window. Kaiser-Bessel window of order N and with parameter beta.
        N, beta = kaiserord(self.stopband_attenuation_dB, self.transition_width)
        nyquist_frequency = self.acquisition_frequency / 2.0
        fir_coefficients = firwin(
            N,
            self.cutoff_frequency / (nyquist_frequency),
            window=("kaiser", beta),  # type: ignore (type hint is incorrect in SciPy)
        )

        # use the filter (NOTE: the `filtfilt` function undoes the delay created by the `lfilter` function we used previously)
        filtered_signal: np.ndarray = filtfilt(fir_coefficients, 1.0, raw_signal)
        return time, filtered_signal


@dataclass
class MovingAverageFiler(Filter):
    r"""
    Sliding window filter
    ---
    Time-domain impulse response:
    h[n] = 1/M for  0<=n<=M , 0 else

    Window size is calculated based on the desired time window and acquisition frequency as:
    M = T * f_acq

    Hence, the output signal y[n] is calculated from the input signal x[n] using
    y[n] = \frac{1}{M} \sum_{k=0}^{M-1} x[n-k]

    NOTE: To deal with the first M windows, the average is taken over the available points,
         effectively ramping up the size M at the beginning and scaling it down at the end.
    """

    time_window: float
    acquisition_frequency: float = 58.0

    def __post_init__(self):
        """Determine window size upon instantiation"""
        self._window_size = int(self.time_window * self.acquisition_frequency)

    def filter(
        self, time: NDArray[np.floating], raw_signal: NDArray[np.floating]
    ) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
        """apply the moving average filter to a single time trace. "signal" is the value array named self.coordinate."""
        M = self._window_size
        filtered_signal = []
        for n in range(len(raw_signal)):
            start = max(0, n - M + 1)
            filtered_signal.append(np.mean(raw_signal[start : (n + 1)]))

        filtered_signal = np.array(filtered_signal)
        return time, filtered_signal
