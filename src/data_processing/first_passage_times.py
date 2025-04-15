"""
!Decide if this is considered specific to primer-extension experiments...
"""

from dataclasses import dataclass

import numpy as np

from data_types.time_trace import TimeTrace
from src.data_processing.transformation import Transformation


@dataclass
class FirstPassageTimes(Transformation):
    """
    returns array of first-passage times of the specified coordinate of the TimeTrace at checkpoints set by the window size.
    Window size is in arbitrary units, set it appropriately depending on the type of signal you are looking at.
    NOTE: This means it does not only pertain to nucleotide positions.


    !! DETERMINE APPROPRIATE OUTPUT / RETURN TYPE AS WE CAN NO LONGER TREAT THIS AS A TRANSFORMATION OF TIMETRACE TO TIMETRACE !!
    """

    coordinate: str
    window_size: int | float

    def apply(self, trace_list: list[TimeTrace]) -> list[TimeTrace]:
        traces_to_edit = [
            trace for trace in trace_list if trace.ID in self.target_traces
        ]
        for target in traces_to_edit:
            if self.coordinate not in target._value_names:
                raise AttributeError(
                    f"Time trace {target.ID} has no value attributed named {self.coordinate}"
                )
            value_array = getattr(target, self.coordinate)
            time_array = target.t
            first_passage_times = self.determine_first_passage_times(
                signal_values=value_array, time=time_array
            )

        return NotImplemented

    def determine_first_passage_times(
        self, signal_values: np.ndarray, time: np.ndarray
    ) -> np.ndarray:
        """
        first time the array passes the checkpoints set by the windows
        """

        # loop through the trace and record the frame numbers when it passes a target
        start_index = 0
        indices_fpt = []
        while start_index <= (len(signal_values) - self.window_size):
            end_index = np.where(
                signal_values >= signal_values[start_index] + self.window_size
            )[0][0]
            indices_fpt.append(end_index)
            start_index = end_index

        first_passage_times = time[indices_fpt]
        return first_passage_times
