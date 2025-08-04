"""
Core class to define a single (time-) trace
Abstraction is used to define a time trace as anything that has a time array + any number of value arrays of equal length.

- Misha, Jan 2025
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from time_trace_tools.data_types.exception_definitions import InvalidTimeTraceError
from time_trace_tools.data_types.trace_operations import (
    add,
    add_constant_value,
    multiply_by_value,
    subtract,
)
from time_trace_tools.data_types.type_definitions import TimeTraceType

Scalar = int | float | np.integer | np.floating


@dataclass
class TimeTrace(ABC):
    """
    Defines a generic time trace.
    Generally speaking, a time trace is anything that has a time array and any number of equally sized value arrays.
    traces can have labels assigned to them, or to a part of the trace.

    ----------
    Abstract base class, so still needs specific implementations
    !: Inherit only as dataclass when setting @dataclass(eq=False) in the decorator to ensure proper '==' is implemented as done in this class
    """

    ID: str
    t: NDArray[np.floating]
    labels: list[str] = field(default_factory=list)
    section_labels: dict[tuple[int, int], list[str]] = field(default_factory=dict)

    @property
    @abstractmethod
    def _values(self) -> tuple[NDArray[np.floating], ...]:
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

    def __eq__(self, other: object) -> bool:
        """
        Overload the '==' operator to properly deal with the numpy arrays
        ---
        Even though dataclasses automatically create the comparison operator '==' (through __eq__()), we need to modify it as we
        want to correctly compare fields with NumPy arrays. By default array1 == array2 will create an array of booleans (element-wise comparison).
        To get an unambiguous comparison of two time traces, we need to tell it to check if the entirety of those arrays are equal.
        """
        # If the other object is not the same subclass of TimeTrace, we immediately know if cannot be equal
        if not isinstance(other, TimeTrace):
            return NotImplemented

        # now we established they are both instances of the same class
        # now compare all fields other than the value arrays
        for element in fields(self):
            is_not_a_value_array = element.name not in self._value_names
            is_not_time_array = element.name != "t"
            is_not_equal = getattr(self, element.name) != getattr(other, element.name)
            if is_not_a_value_array and is_not_time_array and is_not_equal:
                return False

        # now we compared all non-value arrays for equality (__eq__() works properly on other stuff, just numpy arrays give an issue at times).
        # now we check if the time arrays are equal
        if not np.array_equal(self.t, other.t):
            return False

        # all that is left is to compare if the entirety of each value is equal to its counterpart
        for own_array, other_array in zip(self._values, other._values):  # type: ignore
            if not np.array_equal(own_array, other_array):
                return False

        # If you make it passed all these checks --> Congratulations! the two objects are equal. So if you did not exit the code before now, the answer must be 'True'
        return True

    def __len__(self) -> int:
        """
        Overload the 'len()' method, so that when asking for the length of a time trace, it returns the number of time frames
        """
        return len(self.t)

    def __add__(self, other: TimeTrace | Scalar) -> TimeTrace:
        """
        Overload the addition '+' operator for convenience
        """
        if isinstance(other, TimeTrace):
            return add(self, other)

        elif isinstance(other, Scalar):
            return add_constant_value(self, other)

        else:
            return NotImplemented

    def __radd__(self, other: Scalar) -> TimeTrace:
        """
        implement 'Scalar + TimeTrace' for commutativity of '+' operator
        """
        if isinstance(other, Scalar):
            return self.__add__(other)
        else:
            return NotImplemented

    def __sub__(self, other: TimeTrace | Scalar) -> TimeTrace:
        """
        Overload the subtraction '-' operator for convenience
        """
        if isinstance(other, TimeTrace):
            return subtract(self, other)

        elif isinstance(other, Scalar):
            # add -1 * value is the same as subtracting the value itself
            negative_value = -1 * other
            return add_constant_value(self, negative_value)

        else:
            return NotImplemented

    def __mul__(self, other: Scalar) -> TimeTrace:
        """
        Overload the multiplication '*' operator for convenience
        """
        if isinstance(other, Scalar):
            return multiply_by_value(self, other)
        else:
            return NotImplemented

    def __rmul__(self, other: Scalar) -> TimeTrace:
        """
        implement 'Scalar * TimeTrace' for commutativity of '*' operator
        """
        if isinstance(other, Scalar):
            return self.__mul__(other)
        else:
            return NotImplemented

    def __truediv__(self, other: Scalar) -> TimeTrace:
        """
        Overload the multiplication '/' operator for convenience
        """
        if isinstance(other, Scalar):
            inverse_of_number = other ** (-1)
            return multiply_by_value(self, inverse_of_number)
        else:
            return NotImplemented

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
        elif label not in self.section_labels[key]:
            # simply append to the list, only if this label is not a duplicate
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

    def create_time_trace_for_section(
        self: TimeTraceType,
        start_index: int,
        end_index: int,
        new_id: Optional[str] = None,
    ) -> TimeTraceType:
        """
        create a new time trace with values based on the given section
        """

        if not new_id:
            new_id = self.ID

        section_values = tuple(value[start_index:end_index] for value in self._values)
        return self.__class__(
            ID=new_id,
            t=self.t[start_index:end_index],
            labels=[],
            section_labels={},
            **dict(zip(self._value_names, section_values)),
        )

    def _fetch_indices_section_by_label(self, label: str) -> list[tuple[int, int]]:
        """
        return the section indices that have a particular label
        """

        found_sections: list[tuple[int, int]] = []
        for (start_index, end_index), labels in self.section_labels.items():
            if label in labels:
                found_sections.append((start_index, end_index))
        return found_sections

    def create_sections_by_label(
        self: TimeTraceType, label: str
    ) -> list[TimeTraceType]:
        """
        creates a new list of  TimeTrace instances. Corresponding values are those of the sections with the specified label.

        new name of this trace will be the specified label
        """

        trace_sections = []
        section_indices = self._fetch_indices_section_by_label(label)
        for start_index, end_index in section_indices:
            trace_subset = self.create_time_trace_for_section(
                start_index, end_index, new_id=label
            )
            trace_sections.append(trace_subset)
        return trace_sections
