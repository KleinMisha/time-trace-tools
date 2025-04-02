from dataclasses import dataclass, field

from src.data_processing.transformation import Transformation
from src.data_types.experiment import Experiment


@dataclass
class ExperimentProcessor:
    """
    ExperimentProcessor class keeps track of the set of Transformations to perform, applying the transforms is delayed until an explicit call to `transform_traces()`
    this way you can change your workflow by undoing/redoing transforms as many times as you want (as it under the hood just reproduces the series of events starting from the initial state)
    """

    experiment: Experiment
    transformations: list[Transformation] = field(default_factory=list)
    state_index: int = 0

    def register(self, transformation: Transformation) -> None:
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

    def transform_traces(self) -> None:
        """
        Only when you call this function will things actually be computed.
        You compute it up until the state index
        """
        for transformation in self.transformations[: self.state_index]:
            transformation.apply()
