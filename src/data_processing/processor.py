from copy import deepcopy
from dataclasses import dataclass, field
from typing import Iterable

from src.data_processing.transformation import Transformation
from src.data_types.experiment import Experiment
from src.data_types.time_trace import TimeTrace


@dataclass
class ExperimentProcessor:
    """
    ExperimentProcessor class keeps track of the set of Transformations to perform, applying the transforms is delayed until an explicit call to `run()`
    this way you can change your workflow by undoing/redoing transforms as many times as you want (as it under the hood just reproduces the series of events starting from the initial state)
    """

    original_experiment: Experiment
    transformations: list[Transformation] = field(default_factory=list)
    state_index: int = 0
    _current_experiment: Experiment = field(init=False)

    def add_transformations(self, transformations: Iterable[Transformation]) -> None:
        """Register the entire batch of transformations to make defining a pipeline more convenient."""
        for transformation in transformations:
            self.add_transformation(transformation)

    def add_transformation(self, transformation: Transformation) -> None:
        """
        Register a (single) new Transformation.
        NOTE: If you undid a transformation (without redoing it), you will at this point 'confirm you actually never wanted to perform that operation'. After registering, we
        assume you want to point to the latest transformation.
        """
        del self.transformations[self.state_index :]
        self.transformations.append(transformation)
        self.state_index += 1

    def undo(self) -> None:
        """
        simply move pointer back by one (unless you are already pointing to the first Transformation)
        """
        if self.state_index > 0:
            self.state_index -= 1

    def redo(self) -> None:
        """
        simply move pointer forward by one (unless there you are already pointing to the last Transformation)
        """
        if self.state_index < len(self.transformations):
            self.state_index += 1

    def run(self) -> None:
        """
        Only when you call this function will things actually be computed.
        You compute it up until the state index
        """
        # start fresh / from initial state
        traces = deepcopy(self.original_experiment.traces)
        for transformation in self.transformations[: self.state_index]:
            # keep updating the traces.
            traces = transformation.apply(traces)

        # NOTE: the __class__() method will give type of Experiment this particular implementation is
        id = self.original_experiment.ID
        self._current_experiment = self.original_experiment.__class__(
            ID=id, traces=traces
        )

    def get_current_experiment(self) -> Experiment:
        return self._current_experiment

    def get_current_traces(self) -> list[TimeTrace]:
        return self._current_experiment.traces
