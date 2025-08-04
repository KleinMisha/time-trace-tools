from dataclasses import dataclass
from typing import Optional

from time_trace_tools.data_processing.transformation import (
    BaseTransformation,
    CoordinateTransformation,
)
from time_trace_tools.data_types.type_definitions import TimeTraceType


@dataclass
class MockTransformation(BaseTransformation):
    """
    Does not perform actual useful transform, just to test if it correctly applies only to specified traces
    """

    target_traces: Optional[list[str]]
    coordinate: None = None

    def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
        """NOTE how much simplier this becomes now all checking if a trace is a target and such is moved into the BaseTransformation"""
        trace.__setattr__("applied", True)
        return trace


@dataclass
class MockCoordinateTransformation(CoordinateTransformation):
    """sets all values along given axis equal to 42. Tests workings of coordinate-specific operations"""

    target_traces: Optional[list[str]]
    coordinate: str

    def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
        trace.__setattr__(self.coordinate, [42.0] * len(trace))
        return trace
