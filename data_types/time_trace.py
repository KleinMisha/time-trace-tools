"""
Core class to define a single (time-) trace
Abstraction is used to define a time trace as anything that has a time array + any number of value arrays of equal length.

- Misha, Jan 2025
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar

import numpy as np

TimeTraceType = TypeVar("TimeTraceType", bound="TimeTrace")


# custom error to improve readability a bit
class InvalidTimeTraceError(Exception):
    pass


@dataclass
class TimeTrace(ABC):
    """
    Defines a generic time trace.
    Generally speaking, a time trace is anything that has a time array and any number of equally sized value arrays.
    traces can have labels assigned to them, or to a part of the trace.
    ---------
    Abstract base class, so still needs specific implementations
    """

    ID: str
    t: np.ndarray
    labels: list[str] = field(default_factory=list)
    section_labels: dict[tuple[int, int], list[str]] = field(default_factory=dict)

    @property
    @abstractmethod
    def _values(self) -> tuple[np.ndarray, ...]:
        """
        return all the value arrays as a tuple.
        See subclasses for specific implementation
        """

    @property
    @abstractmethod
    def _value_names(self) -> tuple[str, ...]:
        """
        return a tuple of the names of the values. Should be same as the variable names
        used to instantiate class instance.
        """

    def _validate_array_lengths(self) -> None:
        for i, value_array in enumerate(self._values):
            if not len(value_array) == len(self.t):
                raise InvalidTimeTraceError(
                    f"All values must have the same length as t. Expected {len(self.t)}, but {i}-th value has length of {len(value_array)}"
                )

    def __post_init__(self) -> None:
        """
        this function will automatically be executed when creating a TimeTrace (or an instance of a class inheriting from it).
        dataclasses automatically creates things like the `__init__()` method. Hence, if you want something to happen straight after that
        you use the `__post_init__()` method when working with dataclasses.
        """
        _ = self._values  # make sure to instantiate this attribute
        self._validate_array_lengths()

    def __len__(self) -> int:
        """overwrite the 'len()' method, so that when asking for the length of a time trace, it returns the number of time frames"""
        return len(self.t)

    def add_labels(self, labels: list[str]) -> None:
        self.labels.extend(labels)

    def remove_labels(self, labels: list[str]) -> None:
        for lbl in labels:
            self.labels.remove(lbl)

    def add_labelled_section(
        self, start_index: int, end_index: int, label: str
    ) -> None:
        key = (start_index, end_index)
        if key not in self.section_labels:
            # if this is the first time labelling this section
            new_section = {key: [label]}
            self.section_labels.update(new_section)
        else:
            # simply append to the list
            self.section_labels[key].append(label)

    def add_labelled_sections_from_dictionary(
        self, section_labels: dict[tuple[int, int], list[str]]
    ) -> None:
        """
        Batch add section labels from a dictionary.
        Calls the `add_labelled_section()` method that will check if this is a new section or an new label
        for an existing section
        """

        for (start_index, end_index), label_list in section_labels.items():
            for label in label_list:
                self.add_labelled_section(start_index, end_index, label)

    def remove_labels_from_section(
        self, start_index: int, end_index: int, labels: list[str]
    ) -> None:
        key = (start_index, end_index)
        for lbl in labels:
            self.section_labels[key].remove(lbl)

    def remove_all_labels_from_section(self, start_index: int, end_index: int) -> None:
        key = (start_index, end_index)
        self.section_labels.pop(key)

    def remove_all_sections_by_label(self, label: str) -> None:
        after_deletion = {
            (start_index, end_index): values
            for (start_index, end_index), values in self.section_labels.items()
            if values.count(label) == 0
        }
        self.section_labels = after_deletion
