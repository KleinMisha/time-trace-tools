"""
unit tests for Experiment base class
"""

from copy import copy
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

from tests.data_types.mock_experiment import (
    MockExperiment,
    create_mock_dataset,
    parse_mock_dataset,
)


@pytest.fixture
def number_of_traces() -> int:
    return 100


@pytest.fixture
def experiment(number_of_traces: int) -> MockExperiment:
    """
    generate a mock Experiment
    """
    exp = MockExperiment(ID="mock")
    data = create_mock_dataset(number_traces=number_of_traces)
    one, two, time = parse_mock_dataset(data)
    exp._raw_data = one, two, time
    exp.create_traces_from_raw_data()
    return exp


@pytest.fixture
def mock_data_file(tmp_path: Path, number_of_traces: int) -> Path:
    data_table = create_mock_dataset(number_traces=number_of_traces)
    file_path = tmp_path / "mock_data.txt"
    np.savetxt(file_path, data_table, delimiter=",")
    return file_path


def read_mock_datafile(
    filepath: Path | str,
) -> tuple[NDArray[np.floating], NDArray[np.floating], NDArray[np.floating]]:
    data_table = np.loadtxt(filepath, delimiter=",")
    return parse_mock_dataset(data_table)


def test_create_traces_from_raw_data(experiment: MockExperiment) -> None:
    data = create_mock_dataset()
    one, two, time = parse_mock_dataset(data)
    experiment._raw_data = one, two, time
    experiment.create_traces_from_raw_data()

    for value_one, value_two, trace in zip(one.T, two.T, experiment.traces):
        assert all(trace.value_one == value_one) and all(trace.value_two == value_two)


def test_length_of_experiment(
    experiment: MockExperiment, number_of_traces: int
) -> None:
    assert len(experiment) == number_of_traces


def test_add_traces(experiment: MockExperiment) -> None:
    """
    to test if we can successfully add new traces, we can also just try adding the already existing traces as a new list
    """
    trace_list = experiment.traces.copy()
    experiment.add_traces(trace_list)
    assert len(experiment) == 2 * len(trace_list)


def test_fetch_trace(experiment: MockExperiment) -> None:
    trace_id = "trace_1"
    trace_found = experiment.fetch_trace(trace_id)
    assert trace_found.ID == trace_id


def test_remove_trace(experiment: MockExperiment) -> None:
    trace_id = "trace_1"
    before = copy(experiment)
    experiment.remove_trace(trace_id)
    after = copy(experiment)
    assert len(before) == len(after) + 1
    with pytest.raises(KeyError):
        after.fetch_trace(trace_id)


def test_fetch_traces_by_label(experiment: MockExperiment) -> None:
    first_label = "first label"
    trace = experiment.fetch_trace(trace_id="trace_1")
    trace.add_labels([first_label])
    assert len(experiment.fetch_traces_by_label(first_label)) == 1
    assert experiment.fetch_traces_by_label(first_label)[0] == trace


def test_fetch_traces_multiple_labels(experiment: MockExperiment) -> None:
    """
    if you have two labels divided over three traces, do things still work as expected?
    """
    first_label = "first label"
    second_label = "second label"
    trace1 = experiment.fetch_trace(trace_id="trace_1")
    trace1.add_labels([first_label, second_label])
    trace2 = experiment.fetch_trace(trace_id="trace_2")
    trace2.add_labels([first_label])
    trace3 = experiment.fetch_trace(trace_id="trace_3")
    trace3.add_labels([second_label])

    assert len(experiment.fetch_traces_by_label(first_label)) == 2
    assert len(experiment.fetch_traces_by_label(second_label)) == 2
    assert experiment.fetch_traces_by_label(first_label) == [trace1, trace2]
    assert experiment.fetch_traces_by_label(second_label) == [trace1, trace3]


def test_load_raw_data(experiment: MockExperiment, mock_data_file: Path) -> None:
    experiment.load_raw_data(path=mock_data_file, data_loader_fn=read_mock_datafile)
    read_directly = read_mock_datafile(filepath=mock_data_file)
    for array_method, array_direct in zip(experiment._raw_data, read_directly):
        assert np.array_equal(array_method, array_direct)


def test_add_common_labelled_section_from_dictionary(
    experiment: MockExperiment,
) -> None:
    """
    test if all traces correctly get assigned the section labels.
    The function on the TimeTrace level is already tested by itself.
    """
    my_sections = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
        (0, 9): ["second label"],
    }

    has_first_label = [(0, 3), (4, 6)]
    has_second_label = [(4, 6), (0, 9)]
    experiment.add_common_labelled_section_from_dictionary(section_labels=my_sections)
    for time_trace in experiment.traces:
        assert (
            time_trace._fetch_indices_section_by_label(label="first label")
            == has_first_label
        )
        assert (
            time_trace._fetch_indices_section_by_label(label="second label")
            == has_second_label
        )


def test_add_batch_labels_from_dictionary(experiment: MockExperiment) -> None:
    """
    add a label to a bunch of traces at once
    """
    my_labels = {
        "trace_1": ["first_label", "second_label"],
        "trace_50": ["second_label", "third_label"],
        "trace_13": ["first_label", "fourth_label"],
    }
    experiment.set_labels(labels=my_labels)

    trace_1 = experiment.fetch_trace(trace_id="trace_1")
    trace_50 = experiment.fetch_trace(trace_id="trace_50")
    trace_13 = experiment.fetch_trace(trace_id="trace_13")

    has_first_label = [trace_1, trace_13]
    has_second_label = [trace_1, trace_50]
    has_third_label = [trace_50]
    has_fourth_label = [trace_13]

    assert experiment.fetch_traces_by_label(label="first_label") == has_first_label
    assert experiment.fetch_traces_by_label(label="second_label") == has_second_label
    assert experiment.fetch_traces_by_label(label="third_label") == has_third_label
    assert experiment.fetch_traces_by_label(label="fourth_label") == has_fourth_label


def test_get_labels(experiment: MockExperiment) -> None:
    """should be trivial, just here to ensure function does not get removed unintentionally / increase coverage"""
    my_labels = {
        "trace_1": ["first_label", "second_label"],
        "trace_50": ["second_label", "third_label"],
        "trace_13": ["first_label", "fourth_label"],
    }
    experiment.set_labels(labels=my_labels)

    assert experiment.get_labels() == {
        trace.ID: my_labels[trace.ID] if trace.ID in my_labels.keys() else []
        for trace in experiment.traces
    }


def test_get_labels_empty(experiment: MockExperiment) -> None:
    assert experiment.get_labels() == {trace.ID: [] for trace in experiment.traces}


def test_add_batch_section_labels(experiment: MockExperiment) -> None:
    """Using the experiment to set labels on individual traces"""
    my_section_labels = {
        "trace_23": {
            (0, 10): ["start", "first_label"],
            (23, 42): ["first_label", "second_label"],
        },
        "trace_45": {
            (32, 60): ["start", "first_label"],
            (75, 80): ["second_label"],
        },
    }
    experiment.set_section_labels(my_section_labels)
    trace_23 = experiment.fetch_trace("trace_23")
    trace_45 = experiment.fetch_trace("trace_45")
    assert trace_23._fetch_indices_section_by_label(label="start") == [(0, 10)]
    assert trace_23._fetch_indices_section_by_label(label="first_label") == [
        (0, 10),
        (23, 42),
    ]
    assert trace_23._fetch_indices_section_by_label(label="second_label") == [(23, 42)]

    assert trace_45._fetch_indices_section_by_label(label="start") == [(32, 60)]
    assert trace_45._fetch_indices_section_by_label(label="first_label") == [(32, 60)]
    assert trace_45._fetch_indices_section_by_label(label="second_label") == [(75, 80)]


def test_get_section_labels(experiment: MockExperiment) -> None:
    """should be trivial, just here to ensure function does not get removed unintentionally / increase coverage"""
    my_section_labels = {
        "trace_23": {
            (0, 10): ["start", "first_label"],
            (23, 42): ["first_label", "second_label"],
        },
        "trace_45": {
            (32, 60): ["start", "first_label"],
            (75, 80): ["second_label"],
        },
    }
    experiment.set_section_labels(my_section_labels)
    assert experiment.get_section_labels() == {
        trace.ID: my_section_labels[trace.ID]
        if trace.ID in my_section_labels.keys()
        else {}
        for trace in experiment.traces
    }


def test_get_section_labels_empty(experiment: MockExperiment) -> None:
    assert experiment.get_section_labels() == {
        trace.ID: {} for trace in experiment.traces
    }


def test_fetch_non_existing_trace(experiment: MockExperiment) -> None:
    with pytest.raises(KeyError):
        experiment.fetch_trace(trace_id="non existing")


def test_fetch_non_existing_label(experiment: MockExperiment) -> None:
    assert len(experiment.fetch_traces_by_label(label="non existing")) == 0
