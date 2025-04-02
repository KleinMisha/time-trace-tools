from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.data_types.time_trace import TimeTrace


@dataclass
class Transformation(ABC):
    """
    A generic operation you perform on a TimeTrace that produces another TimeTrace
    NOTE: Dependency injection --> only dependencies on generic TimeTraces and Experiments, not on specific implementations
    """

    target_traces: list[TimeTrace]

    @abstractmethod
    def apply(self) -> list[TimeTrace]:
        """
        apply transformation on the target traces to produce new set of traces
        """
        ...
