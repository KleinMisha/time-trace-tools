"""
Core class to define a series of experiments (each containing a series of traces)

"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

from time_trace import NotATimeTraceError, TimeTrace


@dataclass
class Experiment(ABC):
    """
    will populate later
    """

    ID: str
    traces: list[TimeTrace] = field(default_factory=list)
    path_to_raw_data: str = ""
    experimental_conditions: dict[str, Any] = field(default_factory=dict)

    def load_raw_data(self, path: str, data_loader_fn: Callable[[str], Any]) -> None:
        """
        Implement how the raw dat is loaded using the `data_loader_fn` method.

        In stead of a return, set the `._raw_data` attribute
        """
        raw_data = data_loader_fn(path)
        self._raw_data = raw_data

    @abstractmethod
    def _create_trace_list_from_raw_data(self) -> list[TimeTrace]:
        """
        Implement how the traces should be instantiated based on the loaded raw data
        As data from different experiments might have different structures, intentionally left this as abstract method
        """
        pass

    def create_traces_from_raw_data(self) -> None:
        trace_list = self._create_trace_list_from_raw_data()
        self.traces = trace_list

    def add_traces(self, trace_list: list[TimeTrace]) -> None:
        self.traces.extend(trace_list)

    def remove_trace(self, trace_id: str) -> None:
        after_removal = [trace for trace in self.traces if trace.ID != trace_id]
        self.traces = after_removal

    def fetch_trace(self, trace_id: str) -> TimeTrace:
        for trace in self.traces:
            if trace.ID == trace_id:
                return trace
        raise NotATimeTraceError(
            f"Experiment does not contain TimeTrace with ID {trace_id}"
        )

    def fetch_traces_by_label(self, label: str) -> list[TimeTrace]:
        return [trace for trace in self.traces if label in trace.labels]

    def __len__(self) -> int:
        return len(self.traces)
