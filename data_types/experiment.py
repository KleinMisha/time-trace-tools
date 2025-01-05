"""
Core class to define an experiment (containing a series of traces)

"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from time_trace import TimeTrace


@dataclass
class Experiment(ABC):
    """
    A generic ('abstract') definition of an experiment
    """

    ID: str
    traces: list[TimeTrace] = field(default_factory=list)
    experimental_conditions: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def load_raw_data(self, filepath: str) -> None:
        pass

    @abstractmethod
    def create_traces_from_raw_data(self) -> None:
        pass

    def add_trace(self, trace: TimeTrace) -> None:
        self.traces.append(trace)
