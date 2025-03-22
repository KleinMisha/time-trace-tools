"""
basic operations that allow us to add, subtract, etc. multiple traces.
Also includes shifting a trace to the left/right
"""

from copy import deepcopy
from typing import Optional

import numpy as np

from src.data_types.exception_definitions import InvalidTimeTraceError
from src.data_types.type_definitions import TimeTraceType

Scalar = int | float | np.integer | np.floating


def _validate_traces_are_equal_length(
    trace_1: TimeTraceType, trace_2: TimeTraceType
) -> None:
    if len(trace_1) != len(trace_2):
        raise InvalidTimeTraceError(
            f"Traces are of unequal length. {trace_1.ID} has a length of {len(trace_1)}, but {trace_2.ID} has a length of {len(trace_2)}"
        )


def _validate_traces_are_of_same_type(
    trace_1: TimeTraceType, trace_2: TimeTraceType
) -> None:
    if not isinstance(trace_1, type(trace_2)):
        raise InvalidTimeTraceError(
            f"Cannot use traces of different kinds. {trace_1.ID} is a {type(trace_1)}, but {trace_2.ID} is a {type(trace_2)}"
        )


def _validate_time_arrays_align(trace_1: TimeTraceType, trace_2: TimeTraceType) -> None:
    if np.any(np.not_equal(trace_1.t, trace_2.t)):
        raise InvalidTimeTraceError(
            f"Time-axis of {trace_1.ID} does not coincide with that of {trace_2.ID}"
        )


def _validate_traces_are_additive(
    trace_1: TimeTraceType, trace_2: TimeTraceType
) -> None:
    """
    Can only add two traces together (or subtract one trace from another) if the two traces:
    - are of the same sub-type (i.e. cannot add a bead height to fluorescence intensity)
    - have an equal number of time points (i.e. len() are equal)
    - their respective time-axis coincide (i.e. the t-array's are equal)
    """
    _validate_traces_are_of_same_type(trace_1, trace_2)
    _validate_traces_are_equal_length(trace_1, trace_2)
    _validate_time_arrays_align(trace_1, trace_2)


def add(
    trace_1: TimeTraceType, trace_2: TimeTraceType, new_id: Optional[str] = None
) -> TimeTraceType:
    """
    Computes trace_1 + trace_2 for all their value arrays
    NOTE: Does not copy over any (section) labels
    """
    # make sure the two traces can actually be added together
    _validate_traces_are_additive(trace_1, trace_2)

    # default value for the ID
    if not new_id:
        new_id = f"{trace_1.ID} + {trace_2.ID}"

    summed_values = tuple(
        value_1 + value_2 for value_1, value_2 in zip(trace_1._values, trace_2._values)
    )

    Trace = type(trace_1)
    return Trace(
        ID=new_id,
        t=deepcopy(trace_1.t),  # validation ensured this is the same as trace_2.t
        labels=[],
        section_labels={},
        **dict(zip(trace_1._value_names, summed_values)),
    )


def subtract(
    trace_1: TimeTraceType, trace_2: TimeTraceType, new_id: Optional[str] = None
) -> TimeTraceType:
    """
    Computes trace_1 - trace_2 for all their value arrays
    NOTE: Does not copy over any (section) labels
    """
    # make sure the two traces can actually be subtracted from each other
    _validate_traces_are_additive(trace_1, trace_2)

    # default value for the ID
    if not new_id:
        new_id = f"{trace_1.ID} - {trace_2.ID}"

    difference_values = tuple(
        value_1 - value_2 for value_1, value_2 in zip(trace_1._values, trace_2._values)
    )

    Trace = type(trace_1)
    return Trace(
        ID=new_id,
        t=deepcopy(trace_1.t),  # validation ensured this is the same as trace_2.t
        labels=[],
        section_labels={},
        **dict(zip(trace_1._value_names, difference_values)),
    )


def add_constant_value(
    trace: TimeTraceType, value: Scalar, new_id: Optional[str] = None
) -> TimeTraceType:
    """
    add/subtract constant value from all value arrays.
    (Section) labels are copied over to the returned trace object
    """
    # default value for the ID
    if not new_id:
        new_id = f"{trace.ID} shifted by {value}"

    shifted_values = tuple(original + value for original in trace._values)
    Trace = type(trace)
    return Trace(
        ID=new_id,
        t=deepcopy(trace.t),
        labels=deepcopy(trace.labels),
        section_labels=deepcopy(trace.section_labels),
        **dict(zip(trace._value_names, shifted_values)),
    )


def multiply_by_value(
    trace: TimeTraceType, value: Scalar, new_id: Optional[str] = None
) -> TimeTraceType:
    """
    Multiply all value arrays by constant value.
    (Section) labels are copied over to the returned trace object
    """
    # default value for the ID
    if not new_id:
        new_id = f"{trace.ID} x {value}"

    multiplied_values = tuple(original * value for original in trace._values)
    Trace = type(trace)
    return Trace(
        ID=new_id,
        t=deepcopy(trace.t),
        labels=deepcopy(trace.labels),
        section_labels=deepcopy(trace.section_labels),
        **dict(zip(trace._value_names, multiplied_values)),
    )


def average_traces(
    trace_list: list[TimeTraceType], new_id: str = "averaged time trace"
) -> TimeTraceType:
    """
    Returns a time trace that is the average of the given time traces.
    NOTE: Does not copy over any (section) labels
    """

    # To compute the average, first add all values together
    summed_trace = deepcopy(trace_list[0])
    for new_trace in trace_list[1:]:
        summed_trace = add(summed_trace, new_trace, new_id=f"added {new_trace.ID}")

    # Next, divide by the number of traces
    number_traces = len(trace_list)
    averaged_trace = multiply_by_value(summed_trace, value=(1.0 / number_traces))
    return averaged_trace
