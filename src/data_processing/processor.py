from copy import deepcopy
from dataclasses import dataclass, field

from src.data_processing.transformation import Transformation
from src.data_types.experiment import Experiment


@dataclass
class ExperimentProcessor:
    """
    ExperimentProcessor class keeps track of the set of Transformations to perform, applying the transforms is delayed until an explicit call to `transform_traces()`
    this way you can change your workflow by undoing/redoing transforms as many times as you want (as it under the hood just reproduces the series of events starting from the initial state)
    """

    original_experiment: Experiment
    transformations: list[Transformation] = field(default_factory=list)
    state_index: int = 0

    def add_transformation(self, transformation: Transformation) -> None:
        """
        register the transformation.
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

    def transform_traces(self) -> Experiment:
        """
        Only when you call this function will things actually be computed.
        You compute it up until the state index
        """
        # start fresh / from initial state
        traces = deepcopy(self.original_experiment.traces)
        for transformation in self.transformations[: self.state_index]:
            # keep updating the traces.
            # NOTE: Edits that are not consecutive --> you would make different ExperimentProcessors for the different workflows
            traces = transformation.apply(traces)

        # NOTE: the __class__() method will give type of Experiment this particular implementation is
        return self.original_experiment.__class__(
            ID=self.original_experiment.ID, traces=traces
        )
