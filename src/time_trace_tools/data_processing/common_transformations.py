"""
set of commands (Transformations) frequently encountered
"""

from copy import deepcopy
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from time_trace_tools.data_processing.transformation import (
    CoordinateTransformation,
    PassThroughTransformation,
)
from time_trace_tools.data_types.type_definitions import TimeTraceType


@dataclass
class SelectTraces:
    """keep only the traces with the desired identifiers"""

    target_traces: list[str]

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
        return [trace for trace in trace_list if trace.ID in self.target_traces]


@dataclass
class SelectTracesByLabels:
    """only keep the traces with a specific (set of) label(s)"""

    target_traces: list[str]
    target_labels: list[str]

    def generate_trace_ids(self, trace_list: list[TimeTraceType]) -> list[str]:
        """helper function that defines the new target traces for the generic SelectTraces"""
        return [
            trace.ID
            for trace in trace_list
            if trace.ID in self.target_traces
            and set(trace.labels) == set(self.target_labels)
        ]

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
        selected_traces = self.generate_trace_ids(trace_list)
        return SelectTraces(selected_traces).apply(trace_list)


@dataclass
class SelectFrames(PassThroughTransformation):
    """
    Cut out a part of the target trace(s) starting/ending at the given frames (every time point in a time trace is one time frame)
    Inherit from `BaseTransformation` to get the passthrough logic: non-target traces get passed on to output
    """

    start_frame: int
    end_frame: int

    def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
        """create a new TimeTrace object containing only the data corresponding to the desired frames"""
        section_of_trace = trace.create_time_trace_for_section(
            start_index=self.start_frame, end_index=self.end_frame
        )
        return section_of_trace


@dataclass
class SelectTimeWindow(PassThroughTransformation):
    """
    Cut out a part of the trace starting/ending at the specified time points
    """

    start_time: float
    end_time: float

    def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
        """Similar logic as SelectFrames, now first need to get nearest frames to selected time points"""
        start_frame, end_frame = self._determine_nearest_frames(trace.t)
        section_of_trace = trace.create_time_trace_for_section(
            start_index=start_frame, end_index=end_frame
        )
        return section_of_trace

    def _determine_nearest_frames(
        self, time_array: NDArray[np.floating]
    ) -> tuple[int, int]:
        """Find nearest frames to specified time points"""
        start_frame = int(np.abs(time_array - self.start_time).argmin())
        end_frame = int(np.abs(time_array - self.end_time).argmin())
        return start_frame, end_frame


@dataclass
class ShiftToOrigin(CoordinateTransformation):
    """
    shift target traces to the origin (such that they start at value 0 at time 0)
    """

    def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
        """return new traces starting from value 0 at time 0"""
        time_array = trace.t
        start_time = trace.t[0]
        time_array -= start_time
        value_array = trace.__getattribute__(self.coordinate)
        starting_value = value_array[0]
        value_array -= starting_value

        shifted_trace = deepcopy(trace)
        shifted_trace.__setattr__("t", time_array)
        shifted_trace.__setattr__(self.coordinate, value_array)
        return shifted_trace
