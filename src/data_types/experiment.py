"""
Core class to define a series of experiments (each containing a series of traces)

"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Generic

from src.data_types.time_trace import TimeTraceType

FilePath = Path | str


@dataclass
class Experiment(ABC, Generic[TimeTraceType]):
    """
    Defines a generic experiment as a container of TimeTrace instances.
    Generally speaking an experiment has a name, and a set of time traces that are loaded
    from a raw data file.
    Additionally, experimental conditions can be added as a dictionary to keep track of additional metadata.

    """

    ID: str
    traces: list[TimeTraceType] = field(default_factory=list)
    path_to_raw_data: FilePath = Path("")
    experimental_conditions: dict[str, Any] = field(default_factory=dict)

    def load_raw_data(
        self, path: FilePath, data_loader_fn: Callable[[FilePath], Any]
    ) -> None:
        """
        Implement how the raw dat is loaded using the `data_loader_fn` method.

        In stead of a return, set the `._raw_data` attribute
        """
        raw_data = data_loader_fn(path)
        self._raw_data = raw_data

    @abstractmethod
    def _create_trace_list_from_raw_data(self) -> list[TimeTraceType]:
        """
        Implement how the traces should be instantiated based on the loaded raw data
        As data from different experiments might have different structures, intentionally left this as abstract method
        """
        pass

    def create_traces_from_raw_data(self) -> None:
        trace_list = self._create_trace_list_from_raw_data()
        self.traces = trace_list

    def add_traces(self, trace_list: list[TimeTraceType]) -> None:
        self.traces.extend(trace_list)

    def remove_trace(self, trace_id: str) -> None:
        after_removal = [trace for trace in self.traces if trace.ID != trace_id]
        self.traces = after_removal

    def fetch_trace(self, trace_id: str) -> TimeTraceType:
        for trace in self.traces:
            if trace.ID == trace_id:
                return trace
        raise KeyError(f"Experiment does not contain TimeTrace with ID {trace_id}")

    def fetch_traces_by_label(self, label: str) -> list[TimeTraceType]:
        return [trace for trace in self.traces if label in trace.labels]

    def add_common_labelled_section_from_dictionary(
        self, section_labels: dict[tuple[int, int], list[str]]
    ) -> None:
        """
        Add a batch of section_labels to all member traces.
        Uses the `add_labelled_section()` method that will check if you are adding a new section or a new label to an
        existing section
        """
        for trace in self.traces:
            trace.add_labelled_sections_from_dictionary(section_labels)

    def add_batch_labels_from_dictionary(self, labels: dict[str, list[str]]) -> None:
        """
        Add a batch of labels to selected member traces

        labels [dict[str, list[str]]]: Dictionary mapping trace IDs to lists of labels to be added to it.
        """

        for trace_id, label_list in labels.items():
            trace = self.fetch_trace(trace_id)
            trace.add_labels(labels=label_list)

    def __len__(self) -> int:
        return len(self.traces)
