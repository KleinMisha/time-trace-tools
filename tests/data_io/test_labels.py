"""
Test (section) labels to file


part of: src/data_io/labels.py
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.time_trace_tools.data_io.labels import (
    _serialize_section_labels,
    read_json,
    write_experiment_labels,
    write_experiment_section_labels,
)
from src.time_trace_tools.data_types.magnetic_tweezers_experiment import (
    MagneticTweezersExperiment,
    MagneticTweezersTrace,
)


@pytest.fixture
def mt_traces(number_traces: int = 5) -> list[MagneticTweezersTrace]:
    """Create a list of mock MagneticTweezersTrace instances"""
    # generate a set of MagneticTweezersTrace instances
    t = np.linspace(0, 100, 10)
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    z = np.array([1.0] * len(t))
    mock_traces = [
        MagneticTweezersTrace(ID=f"bead_{i + 1}", t=t, x=x, y=y, z=z)
        for i in range(number_traces)
    ]
    return mock_traces


@pytest.fixture
def labels() -> dict[str, list[str]]:
    return {
        "bead_1": ["mock"],
        "bead_2": ["mock", "mocker", "most mockiest"],
        "bead_3": [],
        "bead_4": ["sooooo mocky"],
        "bead_5": [],
    }


@pytest.fixture
def sections() -> dict[str, dict[tuple[int, int], list[str]]]:
    return {
        "bead_1": {(0, 2): ["start"], (4, 6): ["mid"], (7, 9): ["end"]},
        "bead_2": {(1, 2): ["start"], (3, 5): ["mid"], (7, 9): ["end", "finish"]},
        "bead_3": {},
        "bead_4": {},
        "bead_5": {},
    }


@pytest.fixture
def mt_experiment(
    mt_traces: list[MagneticTweezersTrace],
    labels: dict[str, list[str]],
    sections: dict[str, dict[tuple[int, int], list[str]]],
) -> MagneticTweezersExperiment:
    """Prepare an experiment with some labels and section labels already assigned"""

    experiment = MagneticTweezersExperiment(ID="mock", traces=mt_traces)
    experiment.set_labels(labels)
    experiment.set_section_labels(sections)
    return experiment


def test_writing_labels_to_file(
    mt_experiment: MagneticTweezersExperiment,
    labels: dict[str, list[str]],
    sections: dict[str, dict[tuple[int, int], list[str]]],
) -> None:
    """Write the labels for all the traces in the experiment to file, then check contents is as expected"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as tmp:
        # write to file
        tmp_path = Path(tmp.name)
        write_experiment_labels(mt_experiment, tmp_path)

        # read back from this file
        labels_read = read_json(tmp_path)

        # check these are identical to input
        assert labels_read == labels


def test_writing_sections_to_file(
    mt_experiment: MagneticTweezersExperiment,
    sections: dict[str, dict[tuple[int, int], list[str]]],
) -> None:
    """Write the section labels for all the traces in the experiment to file, then check contents is as expected"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as tmp:
        # write to file
        tmp_path = Path(tmp.name)
        write_experiment_section_labels(mt_experiment, tmp_path)

        # read back from this file
        sections_read = read_json(tmp_path)

        # check these are identical to input
        assert sections_read == _serialize_section_labels(sections)


def test_serializing_sections(
    sections: dict[str, dict[tuple[int, int], list[str]]],
) -> None:
    """Make sure JSON data is in the expected format"""
    before = {
        "bead_1": {(0, 2): ["start"], (4, 6): ["mid"], (7, 9): ["end"]},
        "bead_2": {(1, 2): ["start"], (3, 5): ["mid"], (7, 9): ["end", "finish"]},
    }
    expected = {
        "bead_1": [
            {"start": 0, "end": 2, "labels": ["start"]},
            {"start": 4, "end": 6, "labels": ["mid"]},
            {"start": 7, "end": 9, "labels": ["end"]},
        ],
        "bead_2": [
            {"start": 1, "end": 2, "labels": ["start"]},
            {"start": 3, "end": 5, "labels": ["mid"]},
            {"start": 7, "end": 9, "labels": ["end", "finish"]},
        ],
    }

    after = _serialize_section_labels(before)
    assert after == expected
