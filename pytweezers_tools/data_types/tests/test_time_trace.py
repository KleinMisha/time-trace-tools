"""
test generic workings of TimeTrace class, using MagneticTweezersTrace as an instance
"""

import numpy as np
import pytest
from magnetic_tweezers_trace import MagneticTweezersTrace
from mock_time_trace import MockTimeTrace
from exception_definitions import InvalidTimeTraceError

Scalar = int | float | np.integer | np.floating


@pytest.fixture
def time_trace() -> MockTimeTrace:
    """
    generate a mock (MagneticTweezers)TimeTrace
    """
    t = np.linspace(0, 100, 10, dtype=np.float64)
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    return MockTimeTrace(ID="mock", t=t, value_one=x, value_two=y)


@pytest.fixture
def scalar() -> Scalar:
    return 10.0


def test_creating_valid_mt_trace(time_trace: MockTimeTrace) -> None:
    print(time_trace)


def test_creating_invalid_mt_trace() -> None:
    ID = "invalid MT trace"
    t = np.linspace(0, 100, 10, dtype=np.float64)
    x = np.random.random(size=len(t) - 2)
    y = np.random.random(size=len(t) - 2)
    z = np.random.random(size=len(t) - 2)

    # Now should raise NotATimeTraceError if I try to instantiate
    with pytest.raises(InvalidTimeTraceError):
        MagneticTweezersTrace(ID, t=t, x=x, y=y, z=z)


def test_len_of_time_trace(time_trace: MockTimeTrace) -> None:
    assert len(time_trace) == len(time_trace.t)


def test_addition(time_trace: MockTimeTrace) -> None:
    """
    test that if I add a time trace to itself, all values get doubled
    """
    new_trace = time_trace + time_trace
    for new_values, original_values in zip(new_trace._values, time_trace._values):
        assert np.all(new_values == original_values + original_values)


def test_subtraction(time_trace: MockTimeTrace) -> None:
    """
    test that if I subtract a trace from itself, all values are zeros
    """
    new_trace = time_trace - time_trace
    for value_array in new_trace._values:
        assert all(value_array == 0.0)


def test_addition_of_constant(time_trace: MockTimeTrace, scalar: Scalar) -> None:
    """
    check that I can properly add a constant value to all values in the trace
    """
    new_trace = time_trace + scalar
    for new_values, original_values in zip(new_trace._values, time_trace._values):
        assert np.all(new_values == original_values + scalar)


def test_subtraction_of_constant(time_trace: MockTimeTrace, scalar: Scalar) -> None:
    """
    check that I can properly add a constant value to all values in the trace
    """
    new_trace = time_trace - scalar
    for new_values, original_values in zip(new_trace._values, time_trace._values):
        assert np.all(new_values == original_values - scalar)


def test_mupltiplication_by_constant(time_trace: MockTimeTrace, scalar: Scalar) -> None:
    """
    test multiplying all values by a constant value
    """
    new_trace = time_trace * scalar
    for new_values, original_values in zip(new_trace._values, time_trace._values):
        assert np.all(new_values == original_values * scalar)


def test_division_by_constant(time_trace: MockTimeTrace, scalar: Scalar) -> None:
    """
    test dividing all values by a constant value
    """
    new_trace = time_trace / scalar
    for new_values, original_values in zip(new_trace._values, time_trace._values):
        assert np.all(new_values == original_values / scalar)


def test_creating_mt_trace_with_label(time_trace: MockTimeTrace) -> None:
    my_label = ["interesting trace"]
    time_trace.add_labels(my_label)
    assert time_trace.labels == my_label


def test_adding_labels_to_mt_trace(time_trace: MockTimeTrace) -> None:
    my_label = ["first label"]
    time_trace.add_labels(my_label)
    time_trace.add_labels(["second label", "third label"])
    assert time_trace.labels == ["first label", "second label", "third label"]


def test_remove_label_mt_trace(time_trace: MockTimeTrace) -> None:
    my_labels = ["first label", "second label", "third label"]
    time_trace.add_labels(my_labels)
    time_trace.remove_labels(["second label"])
    assert time_trace.labels == ["first label", "third label"]


def test_add_labelled_section(time_trace: MockTimeTrace) -> None:
    my_sections = {(0, 3): ["first label"]}
    time_trace.add_labelled_section(start_index=0, end_index=3, label="first label")
    assert time_trace.section_labels == my_sections


def test_add_new_label_to_existing_section(time_trace: MockTimeTrace) -> None:
    my_sections = {(0, 3): ["first label", "second label"]}
    time_trace.add_labelled_section(start_index=0, end_index=3, label="first label")
    time_trace.add_labelled_section(start_index=0, end_index=3, label="second label")
    assert time_trace.section_labels == my_sections


def test_add_labelled_sections_from_dictionary(time_trace: MockTimeTrace) -> None:
    my_sections = {(0, 3): ["first label", "second label"]}
    time_trace.add_labelled_sections_from_dictionary(my_sections)
    assert time_trace.section_labels == my_sections


def test_add_duplicate_labels(time_trace: MockTimeTrace) -> None:
    my_sections = {(0, 3): ["first label", "second label"]}
    time_trace.add_labelled_sections_from_dictionary(my_sections)
    # the .add_labelled_section() should prevent adding sections to a trace that already exist
    time_trace.add_labelled_sections_from_dictionary(my_sections)
    assert time_trace.section_labels == my_sections


def test_remove_label_from_section(time_trace: MockTimeTrace) -> None:
    before = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
        (0, 9): ["second label"],
    }
    time_trace.add_labelled_sections_from_dictionary(section_labels=before)

    time_trace.remove_labels_from_section(
        start_index=4, end_index=6, labels=["first label"]
    )

    after = {
        (0, 3): ["first label"],
        (4, 6): ["second label"],
        (0, 9): ["second label"],
    }
    assert time_trace.section_labels == after


def test_remove_all_sections_by_label(time_trace: MockTimeTrace) -> None:
    before = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
        (0, 9): ["second label"],
    }
    time_trace.add_labelled_sections_from_dictionary(section_labels=before)
    time_trace.remove_all_sections_by_label(label="second label")

    after = {
        (0, 3): ["first label"],
    }
    assert time_trace.section_labels == after


def test_remove_section(time_trace: MockTimeTrace) -> None:
    before = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
        (0, 9): ["second label"],
    }
    time_trace.add_labelled_sections_from_dictionary(section_labels=before)
    time_trace.remove_all_labels_from_section(start_index=0, end_index=9)

    after = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
    }
    assert time_trace.section_labels == after


def test_fetch_indices_section_by_label(time_trace: MockTimeTrace) -> None:
    my_sections = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
        (0, 9): ["second label"],
    }
    time_trace.add_labelled_sections_from_dictionary(section_labels=my_sections)

    has_first_label = [(0, 3), (4, 6)]
    has_second_label = [(4, 6), (0, 9)]

    assert (
        time_trace._fetch_indices_section_by_label(label="first label")
        == has_first_label
    )
    assert (
        time_trace._fetch_indices_section_by_label(label="second label")
        == has_second_label
    )


def test_fetch_section_non_existing_label(time_trace: MockTimeTrace) -> None:
    my_sections = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
        (0, 9): ["second label"],
    }
    time_trace.add_labelled_sections_from_dictionary(section_labels=my_sections)
    assert time_trace._fetch_indices_section_by_label(label="third label") == []
