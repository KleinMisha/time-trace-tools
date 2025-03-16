"""
test generic workings of TimeTrace class, using MagneticTweezersTrace as an instance
"""

import numpy as np
import pytest
from magnetic_tweezers_trace import MagneticTweezersTrace
from time_trace import InvalidTimeTraceError, TimeTrace


@pytest.fixture
def time_trace() -> MagneticTweezersTrace:
    """
    generate a mock MagneticTweezersTrace
    NOTE: Shouldn't use random numbers in a unittest, but given there is no way any of these tests can fail for any possible outcome, I think it is still fine.
    TODO: Avoid using random numbers?
    """
    t = np.linspace(0, 100, 10, dtype=np.float64)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))
    return MagneticTweezersTrace(ID="mock", t=t, x=x, y=y, z=z)


def test_creating_valid_mt_trace(time_trace: TimeTrace) -> None:
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


def test_len_of_time_trace(time_trace: TimeTrace) -> None:
    assert len(time_trace) == len(time_trace.t)


def test_creating_mt_trace_with_label(time_trace: TimeTrace) -> None:
    my_label = ["interesting trace"]
    time_trace.add_labels(my_label)
    assert time_trace.labels == my_label


def test_adding_labels_to_mt_trace(time_trace: TimeTrace) -> None:
    my_label = ["first label"]
    time_trace.add_labels(my_label)
    time_trace.add_labels(["second label", "third label"])
    assert time_trace.labels == ["first label", "second label", "third label"]


def test_remove_label_mt_trace(time_trace: TimeTrace) -> None:
    my_labels = ["first label", "second label", "third label"]
    time_trace.add_labels(my_labels)
    time_trace.remove_labels(["second label"])
    assert time_trace.labels == ["first label", "third label"]


def test_add_labelled_section(time_trace: TimeTrace) -> None:
    my_sections = {(0, 3): ["first label"]}
    time_trace.add_labelled_section(start_index=0, end_index=3, label="first label")
    assert time_trace.section_labels == my_sections


def test_add_new_label_to_existing_section(time_trace: TimeTrace) -> None:
    my_sections = {(0, 3): ["first label", "second label"]}
    time_trace.add_labelled_section(start_index=0, end_index=3, label="first label")
    time_trace.add_labelled_section(start_index=0, end_index=3, label="second label")
    assert time_trace.section_labels == my_sections


def test_add_labelled_sections_from_dictionary(time_trace: TimeTrace) -> None:
    my_sections = {(0, 3): ["first label", "second label"]}
    time_trace.add_labelled_sections_from_dictionary(my_sections)
    assert time_trace.section_labels == my_sections


def test_add_duplicate_labels(time_trace: TimeTrace) -> None:
    my_sections = {(0, 3): ["first label", "second label"]}
    time_trace.add_labelled_sections_from_dictionary(my_sections)
    # the .add_labelled_section() should prevent adding sections to a trace that already exist
    time_trace.add_labelled_sections_from_dictionary(my_sections)
    assert time_trace.section_labels == my_sections


def test_remove_label_from_section(time_trace: TimeTrace) -> None:
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


def test_remove_all_sections_by_label(time_trace: TimeTrace) -> None:
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


def test_remove_section(time_trace: TimeTrace) -> None:
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


def test_fetch_indices_section_by_label(time_trace: TimeTrace) -> None:
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


def test_fetch_section_non_existing_label(time_trace: TimeTrace) -> None:
    my_sections = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
        (0, 9): ["second label"],
    }
    time_trace.add_labelled_sections_from_dictionary(section_labels=my_sections)
    assert time_trace._fetch_indices_section_by_label(label="third label") == []
