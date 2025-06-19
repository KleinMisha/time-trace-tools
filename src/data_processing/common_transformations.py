"""
set of commands (Transformations) frequently encountered
"""

from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from src.data_types.type_definitions import TimeTraceType


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
            if trace.ID in self.target_labels
            and set(trace.labels) == set(self.target_labels)
        ]

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
        selected_traces = self.generate_trace_ids(trace_list)
        return SelectTraces(selected_traces).apply(trace_list)


@dataclass
class SelectFrames:
    """
    Cut out a part of the target trace(s) starting/ending at the given frames (every time point in a time trace is one time frame)
    """

    target_traces: list[str]
    start_frame: int
    end_frame: int

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
        """creates a new set of TimeTrace objects containing only the data corresponding to the desired frames."""
        new_traces = []
        for trace in trace_list:
            if trace.ID in self.target_traces:
                section_of_trace = trace.create_time_trace_for_section(
                    start_index=self.start_frame, end_index=self.end_frame
                )
                new_traces.append(section_of_trace)
            else:
                # NOTE: If the trace is not a target trace, just pass the original onwards.
                #!?Assumes you will explicitly call the SelectTraces operation afterwards. Better than have this one implicitly select the traces as well, correct?
                new_traces.append(trace)
        return new_traces


@dataclass
class SelectTimeWindow:
    """
    Cut out a part of the trace starting/ending at the specified time points
    """

    target_traces: list[str]
    start_time: float
    end_time: float

    def generate_target_frames(
        self, time_array: NDArray[np.floating]
    ) -> tuple[int, int]:
        """Find nearest frames to specified time points"""
        start_frame = int(np.abs(time_array - self.start_time).argmin())
        end_frame = int(np.abs(time_array - self.end_time).argmin())
        return start_frame, end_frame

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
        """
        Call the SelectFrames Transformation
        !Assumes the time vectors are identical for all traces in the list.
        todo: If this is not the case, you must subset each trace differently.
        """
        common_time_array = trace_list[0].t
        start_frame, end_frame = self.generate_target_frames(common_time_array)
        return SelectFrames(self.target_traces, start_frame, end_frame).apply(
            trace_list
        )


@dataclass
class ShiftToOrigin:
    """
    shift target traces to the origin (such that they start at value 0 at time 0)
    !Make sure to unit test that it does not modify the original traces. Should be fine given a deepcopy is passed into this from the ExperimentProcessor
    """

    target_traces: list[str]
    coordinate: str  # should match one of the available ._value_names of the TimeTrace class (e.g. MagneticTweezersTrace has 'x','y','z')

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
        """time-shift the trace along specified coordinate"""

        # quick check you have the coordinate available
        # ? Possible to remove this code / check and just assume the user is not going to ask to shift a trace along an invalid coordinate
        valid_coordinate, invalid_trace = self._traces_have_coordinate(trace_list)
        if not valid_coordinate:
            raise AttributeError(
                f"Trace {invalid_trace} does not have a value-array named {self.coordinate}"
            )

        # the actual operation:
        new_traces = []
        for trace in trace_list:
            if trace.ID in self.target_traces:
                time_array = trace.t
                start_time = trace.t[0]
                time_array -= start_time
                value_array = trace.__getattribute__(self.coordinate)
                starting_value = value_array[0]
                value_array -= starting_value

                shifted_trace = deepcopy(trace)
                shifted_trace.__setattr__("t", time_array)
                shifted_trace.__setattr__(self.coordinate, value_array)
                new_traces.append(shifted_trace)

            else:
                # keep the other traces unaffected.
                new_traces.append(trace)
        return new_traces
