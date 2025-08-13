"""
Core class to define a series of experiments (each containing a series of traces)

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Generic

from numpy.typing import NDArray

from time_trace_tools.data_types.experiment_operations import (
    add,
    add_trace_to_experiment,
    subtract,
    subtract_trace_from_experiment,
)
from time_trace_tools.data_types.time_trace import TimeTrace
from time_trace_tools.data_types.type_definitions import TimeTraceType

FilePath = Path | str
DataLoaderFunction = Callable[[FilePath], tuple[NDArray[Any], ...]]


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

    @abstractmethod
    def _create_trace_list_from_raw_data(self) -> list[TimeTraceType]:
        """
        Implement how the traces should be instantiated based on the loaded raw data
        As data from different experiments might have different structures, intentionally left this as abstract method
        """
        pass

    def __len__(self) -> int:
        return len(self.traces)

    def __add__(
        self, other: Experiment[TimeTraceType] | TimeTraceType
    ) -> Experiment[TimeTraceType]:
        """
        Overload the addition '+' operator for convenience
        """
        if isinstance(other, Experiment):
            return add(self, other)
        elif isinstance(other, TimeTrace):
            return add_trace_to_experiment(self, other)
        else:
            return NotImplemented

    def __sub__(
        self, other: Experiment[TimeTraceType] | TimeTraceType
    ) -> Experiment[TimeTraceType]:
        """
        Overload the addition '-' operator for convenience
        """
        if isinstance(other, Experiment):
            return subtract(self, other)
        elif isinstance(other, TimeTrace):
            return subtract_trace_from_experiment(self, other)
        else:
            return NotImplemented

    def load_raw_data(self, path: FilePath, data_loader_fn: DataLoaderFunction) -> None:
        """
        Implement how the raw dat is loaded using the `data_loader_fn` method.

        In stead of a return, set the `._raw_data` attribute
        """
        raw_data = data_loader_fn(path)
        self._raw_data = raw_data

    def create_traces_from_raw_data(self) -> None:
        trace_list = self._create_trace_list_from_raw_data()
        self.traces = trace_list

    def add_traces(self, trace_list: list[TimeTraceType]) -> None:
        for trace in trace_list:
            self.__add__(trace)

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

    def set_labels(self, labels: dict[str, list[str]]) -> None:
        """
        Set labels for multiple traces within your experiment

        labels [dict[str, list[str]]]: Dictionary mapping trace IDs to lists of labels to be added to it.
        """

        for trace_id, label_list in labels.items():
            trace = self.fetch_trace(trace_id)
            trace.add_labels(labels=label_list)

    def set_section_labels(
        self, section_labels: dict[str, dict[tuple[int, int], list[str]]]
    ) -> None:
        """
        Set section labels for traces within your experiment

        section_labels [dict[str, dict[tuple[int, int], list[str]]]]: Dictionary mapping trace IDs to the dictionary of section labels to be added to it
        """
        for trace_id, section_labels_dict in section_labels.items():
            trace = self.fetch_trace(trace_id)
            trace.add_labelled_sections_from_dictionary(section_labels_dict)

    def get_labels(self) -> dict[str, list[str]]:
        return {trace.ID: trace.labels for trace in self.traces}

    def get_section_labels(self) -> dict[str, dict[tuple[int, int], list[str]]]:
        return {trace.ID: trace.section_labels for trace in self.traces}
