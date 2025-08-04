from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from time_trace_tools.data_types.exception_definitions import InvalidExperimentError
from time_trace_tools.data_types.type_definitions import ExperimentType, TimeTraceType

if TYPE_CHECKING:
    from time_trace_tools.data_types.experiment import Experiment
    from time_trace_tools.data_types.time_trace import TimeTrace


def _validate_all_traces_of_the_same_type(
    experiment: Experiment[TimeTrace], trace: TimeTrace
) -> None:
    if not all([isinstance(trace, type(t)) for t in experiment.traces]):
        raise InvalidExperimentError(
            f"Cannot use traces of different kinds. {trace.ID} is a {type(trace)}, but {experiment.ID} excepts traces of type {type(experiment.traces[0])}"
        )


def _validate_experiments_of_same_type(
    experiment_1: Experiment, experiment_2: Experiment
):
    if not isinstance(experiment_1, type(experiment_2)):
        raise InvalidExperimentError(
            f"Incompatible experiments. {experiment_1.ID} is of type {type(experiment_1)}, but {experiment_2.ID} is of type {type(experiment_2)}"
        )


def add_trace_to_experiment(
    experiment: Experiment[TimeTraceType], trace: TimeTraceType
) -> Experiment[TimeTraceType]:
    """
    add a trace to the current experiment's trace list
    """
    _validate_all_traces_of_the_same_type(experiment, trace)  # type: ignore
    experiment.traces.extend([trace])
    return deepcopy(experiment)


def add(experiment_1: ExperimentType, experiment_2: ExperimentType) -> ExperimentType:
    """
    add all traces of experiment_2 to those of experiment_1.
    Essentially merges the two experiments into a new one.
    """
    _validate_experiments_of_same_type(experiment_1, experiment_2)
    exp_1_plus_2 = deepcopy(experiment_1)
    exp_1_plus_2.traces.extend(experiment_2.traces)
    return exp_1_plus_2


def subtract(
    experiment_1: ExperimentType, experiment_2: ExperimentType
) -> ExperimentType:
    """
    remove all traces of experiment_2 from experiment_1 (experiment_1 - experiment_2)
    Essentially undoes the `add()` operation


    NOTE: dataclasses already implement the __eq__() method, so it should be capable of assessing equality of two time traces out of the box
    """

    difference_trace_list = [
        trace for trace in experiment_1.traces if trace not in experiment_2.traces
    ]
    exp_1_min_2 = deepcopy(experiment_1)
    exp_1_min_2.traces = difference_trace_list
    return exp_1_min_2


def subtract_trace_from_experiment(
    experiment: Experiment[TimeTraceType], trace: TimeTraceType
) -> Experiment[TimeTraceType]:
    """
    remove a trace from the existing experiment
    """
    removed_trace = deepcopy(experiment)
    removed_trace.traces.remove(trace)
    return removed_trace
