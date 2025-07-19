"""
Abstraction(s) for Transformations.


"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol

from src.data_types.type_definitions import TimeTraceType


class Transformation(Protocol):
    """
    A Transformation is any operation that takes a list of TimeTrace objects and returns a new list of TimeTrace objects
    """

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]: ...


class BaseTransformation(ABC):
    """
    Abstract Base Class with optional shared logic.
    Simplifies testing shared logic as it is now localized.
    Also NOTE the subclasses defined below are 100% optional, and merely defined to make development of new Transformation implementations more convenient.
    Hence, this class prevents actual deep inheritance chains (unnecessary coupling).
    """

    def __init__(
        self, target_traces: Optional[list[str]], coordinate: Optional[str]
    ) -> None:
        self.target_traces = target_traces
        self.coordinate = coordinate

    @abstractmethod
    def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
        """Apply the transformation to an individual trace"""

    def _should_transform(self, trace: TimeTraceType) -> bool:
        """
        Checks if the supplied trace is a target of the Transformation.
        If target_traces is an empty list, you will apply the transform to all traces
        """
        if not self.target_traces:
            return True
        return trace.ID in self.target_traces

    def _validate_coordinate_exists(self, trace: TimeTraceType) -> Optional[bool]:
        """Check that the supplied coordinate is a valid name of a property of the time trace."""

        if self.coordinate and self.coordinate not in trace._value_names:
            raise AttributeError(
                f"trace {trace.ID} does not have values named {self.coordinate}"
            )

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
        new_traces = []
        for trace in trace_list:
            if self._should_transform(trace):
                self._validate_coordinate_exists(trace)
                new_traces.append(self.apply_to_one_trace(trace))
            else:
                new_traces.append(trace)
        return new_traces


####### DEFINE CONVENIENT PRESETS BELOW ######


@dataclass
class CoordinateTransformation(BaseTransformation):
    """A Transformation that acts on a particular coordinate"""

    coordinate: str


@dataclass
class AllTracesTransformation(BaseTransformation):
    """No defined target traces, simply works on the full list of traces supplied to the .apply() method"""

    target_traces: None = None
