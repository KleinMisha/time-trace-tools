"""
Interface defining an operation to modify a (set of) target TimeTrace(s)
"""

from typing import Protocol

from src.data_types.type_definitions import TimeTraceType


class Transformation(Protocol):
    """
    Generic operation that adjust time traces, e.g. filtering, translation/rotation, subsection/selecting part of the trace, etc.
    """

    # trace identifiers you want to modify
    target_traces: list[str]

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
        """
        apply transformation on the target traces to produce new set of traces
        NOTE:If traces outside the target list are meant to be kept, ensure these get passed on into the output list (without modifications)
        """
        ...
