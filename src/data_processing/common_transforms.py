"""
set of commands (Transformations) frequently encountered
"""

from copy import deepcopy
from dataclasses import dataclass

from src.data_processing.transformation import Transformation
from src.data_types.time_trace import TimeTrace


@dataclass
class ShiftToOrigin(Transformation):
    """
    shift target traces to the origin (such that they start at value 0 at time 0)
    """

    coordinate: str

    def apply(self) -> list[TimeTrace]:
        before = deepcopy(self.target_traces)
        after = []
        for target in before:
            if self.coordinate in target._value_names:
                time_array = target.t
                start_time = target.t[0]
                time_array -= start_time

                value_array = getattr(target, self.coordinate)
                starting_value = value_array[0]
                value_array -= starting_value

                after.append(target)
        return after


@dataclass
class SelectFrames(Transformation):
    """
    Cut out a part of the target trace(s) starting/ending at the given frames (every time point in a time trace is one time frame)
    """

    start_frame: int
    end_frame: int

    def apply(self) -> list[TimeTrace]:
        part_of_traces = []

        for target in self.target_traces:
            part_of_traces.append(
                target.create_time_trace_for_section(
                    start_index=self.start_frame, end_index=self.end_frame
                )
            )
        return part_of_traces


@dataclass
class SelectTimeWindow(Transformation):
    """
    Cut out a part of the trace starting/ending at the specified time points
    """

    from_time: float
    to_time: float

    def apply(self) -> list[TimeTrace]:
        part_of_traces = []
        for target in self.target_traces:
            # find closest index based on specified time points
            start_index = 0
            end_index = 1

            part_of_traces.append(
                target.create_time_trace_for_section(
                    start_index=start_index, end_index=end_index
                )
            )
        return part_of_traces


@dataclass
class SelectLabeledParts(Transformation):
    """
    Cut out a part(s) of the target trace(s) that are labelled with a `section_label`
    """

    section_label: str

    def apply(self) -> list[TimeTrace]:
        parts_of_traces = []

        for target in self.target_traces:
            for indices in target._fetch_indices_section_by_label(
                label=self.section_label
            ):
                start_index, end_index = indices
                parts_of_traces.append(
                    target.create_time_trace_for_section(
                        start_index=start_index, end_index=end_index
                    )
                )
        return parts_of_traces
