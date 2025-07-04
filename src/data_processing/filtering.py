"""
Common filter Transformations

-- Misha, June 2025
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray
from scipy.signal import filtfilt, firwin, kaiserord

from src.data_processing.transformation import Transformation
from src.data_types.type_definitions import TimeTraceType


@dataclass
class Filter(ABC):
    """A generic Filter Transformation. Gather common functionality in here to avoid duplicate code/ allow for simple testing."""

    target_traces: list[str]
    coordinate: str

    @abstractmethod
    def filter(
        self, time: NDArray[np.floating], raw_signal: NDArray[np.floating]
    ) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
        """Implement the specific filtering operation here. Return (time, filtered_signal)"""

    def _traces_have_coordinate(
        self, trace_list: list[TimeTraceType]
    ) -> tuple[bool, Optional[str]]:
        """check if the coordinate is valid for the given target traces. If not, it will return the first trace ID at which the check fails"""
        targets = [trace for trace in trace_list if trace.ID in self.target_traces]
        for target_trace in targets:
            if self.coordinate not in target_trace._value_names:
                return False, target_trace.ID
        return True, None

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
        """create filtered traces"""

        # Validate coordinate exists for all traces
        valid_coordinate, invalid_trace = self._traces_have_coordinate(trace_list)
        if not valid_coordinate:
            raise AttributeError(
                f"Trace {invalid_trace} does not have a value-array named {self.coordinate}"
            )

        # Loop over trace list and apply filter. Always the same code, independent of the kind of filter
        new_traces = []
        for trace in trace_list:
            if trace.ID in self.target_traces:
                time = trace.t
                value_array = trace.__getattribute__(self.coordinate)
                filtered_time, filtered_values = self.filter(time, value_array)
                filtered_trace = trace
                filtered_trace.__setattr__("t", filtered_time)
                filtered_trace.__setattr__(self.coordinate, filtered_values)
                new_traces.append(filtered_trace)
            else:
                # keep the other traces unaffected
                new_traces.append(trace)

        return new_traces


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
