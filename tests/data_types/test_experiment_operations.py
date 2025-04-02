from copy import deepcopy

import numpy as np
import pytest

from src.data_types.exception_definitions import InvalidExperimentError
from src.data_types.experiment import Experiment
from src.data_types.experiment_operations import (
    add,
    add_trace_to_experiment,
    subtract,
    subtract_trace_from_experiment,
)
from src.data_types.magnetic_tweezers_experiment import MagneticTweezersExperiment
from src.data_types.magnetic_tweezers_trace import MagneticTweezersTrace
from tests.data_types.mock_experiment import (
    MockExperiment,
    create_mock_dataset,
    parse_mock_dataset,
)
from tests.data_types.mock_time_trace import MockTimeTrace


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
def time_trace() -> MockTimeTrace:
    """
    generate a mock (MagneticTweezers)TimeTrace
    """
    t = np.linspace(0, 100, 10)
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    return MockTimeTrace(ID="mock", t=t, value_one=x, value_two=y)


@pytest.fixture
def mt_trace() -> MagneticTweezersTrace:
    t = np.linspace(0, 100, 10, dtype=np.float64)
    x = np.array([1.0] * len(t))
    y = np.array([1.0] * len(t))
    z = np.array([1.0] * len(t))
    return MagneticTweezersTrace(ID="mock", t=t, x=x, y=y, z=z)


@pytest.fixture
def mt_exp() -> MagneticTweezersExperiment:
    return MagneticTweezersExperiment(ID="mock_tweezers")


def test_add_trace_to_experiment(
    experiment: Experiment[MockTimeTrace], time_trace: MockTimeTrace
) -> None:
    original = deepcopy(experiment)
    experiment = add_trace_to_experiment(experiment, time_trace)
    assert len(experiment) == len(original) + 1
    assert experiment.fetch_trace(trace_id=time_trace.ID) == time_trace


def test_addition(experiment: Experiment[MockTimeTrace]) -> None:
    """
    add two copies of the same experiment
    """
    original = deepcopy(experiment)
    experiment = add(experiment_1=experiment, experiment_2=experiment)
    assert len(experiment) == 2 * len(original)


def test_addition_overload(experiment: Experiment[MockTimeTrace]) -> None:
    original = deepcopy(experiment)
    overload = original + original
    no_overload = add(original, original)
    assert all([yes == no for yes, no in zip(overload.traces, no_overload.traces)])


def test_subtraction(experiment: Experiment[MockTimeTrace]) -> None:
    """
    test removing the experiment from itself, should result in empty list
    """
    before = deepcopy(experiment)
    after = subtract(experiment_1=experiment, experiment_2=before)
    assert len(after) == 0


def test_subtraction_of_trace(experiment: Experiment[MockTimeTrace]) -> None:
    """
    remove the first trace from the experiment
    """
    before = deepcopy(experiment)
    trace = experiment.traces[0]
    after = subtract_trace_from_experiment(experiment, trace)
    assert len(after) == len(before) - 1
    assert trace not in after.traces


def test_subtraction_trace_overload(experiment: Experiment[MockTimeTrace]) -> None:
    """
    check using '-' operator works the same as calling the imported function
    """
    trace = experiment.traces[0]
    no_overload = subtract_trace_from_experiment(experiment, trace)
    overload = experiment - trace
    assert all([yes == no for yes, no in zip(overload.traces, no_overload.traces)])


def test_subtraction_overload(experiment: Experiment[MockTimeTrace]) -> None:
    """
    check using '-' operator works the same as calling the imported function
    """
    no_overload = subtract(experiment, experiment)
    overload = experiment - experiment
    assert all([yes == no for yes, no in zip(overload.traces, no_overload.traces)])


def test_invalid_addition_types(experiment: Experiment[MockTimeTrace]) -> None:
    not_allowed_values = [
        True,
        "5",
        [1, 2, 3, 4, 5],
        (1, 2, 3, 4, 5),
        [time_trace, time_trace],
        1.0,
        1,
    ]
    with pytest.raises(TypeError):
        for value in not_allowed_values:
            _ = experiment + value


def test_invalid_subtraction_types(experiment: Experiment[MockTimeTrace]) -> None:
    not_allowed_values = [
        True,
        "5",
        [1, 2, 3, 4, 5],
        (1, 2, 3, 4, 5),
        [time_trace, time_trace],
        1.0,
        1,
    ]
    with pytest.raises(TypeError):
        for value in not_allowed_values:
            _ = experiment - value


def test_incompatible_experiments(
    experiment: Experiment[MockTimeTrace], mt_exp: Experiment[MagneticTweezersTrace]
) -> None:
    with pytest.raises(InvalidExperimentError):
        _ = experiment + mt_exp  # type: ignore


def test_incompatible_trace_with_experiment(
    experiment: Experiment[MockTimeTrace], mt_trace: MagneticTweezersTrace
) -> None:
    with pytest.raises(InvalidExperimentError):
        _ = experiment + mt_trace  # type: ignore
