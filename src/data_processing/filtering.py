"""
Common filter Transformations

-- Misha, June 2025
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray
from scipy.signal import filtfilt, firwin, kaiserord

from src.data_types.type_definitions import TimeTraceType


@dataclass
class KaiserBesselFilter:
    """
    Kaiser-Bessel (low-pass) filter.
    ---
    Typical filter used for polymerase primer-extension traces.
    """

    target_traces: list[str]
    coordinate: str
    acquisition_frequency: float = 58.0
    cutoff_frequency: float = 2.0
    transition_width: float = 0.01  # relative to nyquist frequency. So width in Hz = width * acquisition_frequency /2
    stopband_attenuation_dB: float = 100

    def filter(
        self, time: NDArray[np.floating], signal: NDArray[np.floating]
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
        filtered_signal: np.ndarray = filtfilt(fir_coefficients, 1.0, signal)
        return time, filtered_signal

    # todo: Take care of duplicate code?
    # ? make some 'subtype' of Transformation that acts on a given coordinate? Inherit from Transformation?
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
        # ? Possibly remove this check? Now there is duplicate code
        # todo: take care of duplicate code?
        valid_coordinate, invalid_trace = self._traces_have_coordinate(trace_list)
        if not valid_coordinate:
            raise AttributeError(
                f"Trace {invalid_trace} does not have a value-array named {self.coordinate}"
            )

        new_traces = []
        for trace in trace_list:
            if trace.ID in self.target_traces:
                time = trace.t
                value_array = trace.__getattribute__(self.coordinate)
                filtered_time, filtered_values = self.filter(time, value_array)

                #!CHECK THAT NO COPYING IS NEEDED AS THE EXPERIMENTPROCESSOR TAKES CARE OF THIS. IF NOT TRUE, ADD DEEPCOPY
                filtered_trace = trace
                filtered_trace.__setattr__("t", filtered_time)
                filtered_trace.__setattr__(self.coordinate, filtered_values)
                new_traces.append(filtered_trace)
            else:
                # keep the other traces unaffected
                new_traces.append(trace)

        return new_traces
