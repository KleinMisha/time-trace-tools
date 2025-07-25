"""
Test writing trace data to file


part of: src/data_io/raw_mt.py
"""

import tempfile
from functools import partial
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

from src.data_io.raw_mt import read_pytweezers, write_traces
from src.data_types.magnetic_tweezers_experiment import MagneticTweezersExperiment
from src.data_types.magnetic_tweezers_trace import MagneticTweezersTrace


@pytest.fixture
def number_traces() -> int:
    return 100


@pytest.fixture
def mt_traces(number_traces: int = 100) -> list[MagneticTweezersTrace]:
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
def mt_experiment(mt_traces: list[MagneticTweezersTrace]) -> MagneticTweezersExperiment:
    return MagneticTweezersExperiment(ID="mock", traces=mt_traces)


def create_mt_traces_from_arrays(
    mt_data: tuple[NDArray[np.floating], NDArray[np.floating]],
) -> list[MagneticTweezersTrace]:
    trace_list = []
    bead_positions_xyz: NDArray  # Now Pylance understands .shape is a thing
    bead_positions_xyz, time = mt_data
    num_beads, _, _ = bead_positions_xyz.shape
    for index in range(num_beads):
        x = bead_positions_xyz[index, :, 0]
        y = bead_positions_xyz[index, :, 1]
        z = bead_positions_xyz[index, :, 2]
        bead_nr = index + 1  # We want the first bead to be named number 1, not 0
        trace_id = f"bead_{bead_nr}"

        mt_trace = MagneticTweezersTrace(ID=trace_id, t=time, x=x, y=y, z=z)
        trace_list.append(mt_trace)
    return trace_list


def test_writing_traces_to_file(mt_traces: list[MagneticTweezersTrace]) -> None:
    """Write the list of traces to a file, then read it back to check format is as expected"""

    with tempfile.NamedTemporaryFile(mode="wb+", suffix=".npy") as tmp:
        # write to file
        tmp_path = Path(tmp.name)
        write_traces(mt_traces, tmp_path)

        # read from this file
        dt = np.diff(mt_traces[0].t)[0]
        mt_data = read_pytweezers(tmp_path, acquisition_rate=1.0 / dt)
        traces_read = create_mt_traces_from_arrays(mt_data=mt_data)

    # now check all traces are identical
    for before, after in zip(mt_traces, traces_read):
        assert before == after


def test_creation_experiment_from_written_traces(
    mt_experiment: MagneticTweezersExperiment,
) -> None:
    """Similar, this time starting from MagneticTweezersExperiment and 'reloading your experiment with this file as input'"""
    with tempfile.NamedTemporaryFile(mode="wb+", suffix=".npy") as tmp:
        # write to file
        tmp_path = Path(tmp.name)
        write_traces(mt_experiment.traces, tmp_path)

        # use the file to instantiate a new experiment
        experiment_read = MagneticTweezersExperiment(
            ID="read back from file", path_to_raw_data=tmp_path
        )
        dt = np.diff(mt_experiment.traces[0].t)[0]
        mock_reader = partial(read_pytweezers, acquisition_rate=1.0 / dt)
        experiment_read.load_raw_data(tmp_path, data_loader_fn=mock_reader)
        experiment_read.create_traces_from_raw_data()

    # now check all traces are identical
    for before, after in zip(mt_experiment.traces, experiment_read.traces):
        assert before == after
