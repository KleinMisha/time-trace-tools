from dataclasses import dataclass

import numpy as np
from scipy.signal import firwin, kaiserord, lfilter

from data_types.time_trace import TimeTrace
from src.data_processing.transformation import Transformation


@dataclass
class KaiserBesselFilter(Transformation):
    """
    Kaiser-Bessel filter is the commonly used low-pass filter for magnetic tweezers traces (e.g. traces obtained after primer-extension)
    """

    coordinate: str  # the name of the value array you want to filter
    acquisition_frequency: float
    cutoff_frequency: float
    ripple_db: float = 100.0  # ? What does this do ??
    trans_width: float = 0.01  # ?What does this do ??

    def apply(self, trace_list: list[TimeTrace]) -> list[TimeTrace]:
        traces_to_edit = [
            trace for trace in trace_list if trace.ID in self.target_traces
        ]
        filtered_traces = []
        for target in traces_to_edit:
            if self.coordinate not in target._value_names:
                raise AttributeError(
                    f"Time trace {target.ID} has no value attributed named {self.coordinate}"
                )

            # fetch target value array
            value_array = getattr(target, self.coordinate)
            time = getattr(target, "t")

            # prepare the filter
            nyquist_frequency = self.acquisition_frequency / 2.0
            N, beta = kaiserord(self.ripple_db, self.trans_width)
            taps = firwin(
                N, self.cutoff_frequency / nyquist_frequency, window=("kaiser", beta)
            )
            # in rare cases this value is not quite correct and the filtered trace is shifted compared to the raw trace --> adjust this value
            delay = 0.5 * (N - 1) / self.acquisition_frequency

            # apply the filter
            filtered_values = lfilter(taps, 1.0, value_array)
            new_pos = np.where((time - delay) >= 0)
            new_time = time[new_pos[0][0] :] - delay
            new_values = filtered_values[new_pos[0][0] :]

            # create new trace to append to list
            after_filter = target.__class__(
                ID=target.ID,
                t=new_time,
                labels=target.labels,
                section_labels=target.section_labels,
                **dict(
                    zip(
                        target._value_names,
                        tuple(
                            [
                                np.array([None] * len(new_time))
                                for _ in target._value_names
                            ]
                        ),
                    )
                ),
            )
            setattr(after_filter, self.coordinate, new_values)

            filtered_traces.append(after_filter)
        return filtered_traces


@dataclass
class MovingAverageFilter(Transformation):
    window_size: int

    def apply(self, trace_list: list[TimeTrace]) -> list[TimeTrace]:
        return NotImplemented
