from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.data_types.time_trace import TimeTrace


@dataclass
class Transformation(ABC):
    """
    A generic operation you perform on a TimeTrace that produces another TimeTrace
    NOTE: Dependency injection --> only dependencies on generic TimeTraces and Experiments, not on specific implementations
    """

    # trace identifiers you want to modify
    target_traces: list[str]

    @abstractmethod
    def apply(self, trace_list: list[TimeTrace]) -> list[TimeTrace]:
        """
        apply transformation on the target traces to produce new set of traces
        """
        ...
