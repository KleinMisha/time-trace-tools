### Process time traces 
Having collected your data, and used the `Experiment[TimeTrace]` to represent your data (and do some basic cleanup steps such as selecting the reference bead etc.), now it is time to actually start post-processing your time traces.

This model has the tools to define generic `TimeTrace` processing workflows.
Example operations we would want to perform could be: 
* Cut out a part of the trace 
* Shift (a part of) the trace up or down 
* Filter (a part of) the trace
* Fit a function to part of the trace
* Transform the trace from bead height into a length in nucleotides or a rotation in #turns. 

Some of these operations have been implemented already as part of the `TimeTrace` (or `Experiment`) class for convenience, but others not yet. 

<span style="color:hotpink">**most importantly: we want a flexible system in which we can easily change workflows and undo/redo transformations** </span>

For this reason this module is designed according to the "Command design pattern". 

|<span style="color:lightgrey"> In the Command design pattern the code does not treat the state of the traces after transformations as the 'ground truth', but the combination of the raw data (initial state) and the set of transformations to be performed on the data. Updating the state of the traces is delayed until an explicit call to the `apply` or `excecute` method. This is a common way software is written for non-destructive editors (e.g. video or photo editors) that greatly simplifies implementing `undo` and `redo` behavior. Just as a video editing software does not actually need to show you the final video until you render it, we technically only need to know the raw data and how to get from the raw data to your final result. The result itself is only needed at the end. </span>

| <span style="color:lightgrey"> A smart 'cache' system can be used when many transformations must be performed to quickly intialise your workflow to not start from the raw data, but from some intermediate state if so required. Essentially, you would tell the `Controller` or `DataProcessor`to use a special type of `Transformation` that already produces some intermediate form of your time traces. 



The basic unit we work with will be a `Transformation`: A class with some parameters used in a method that takes in a `TimeTrace` and returns another `TimeTrace`. 

```python
from abc import ABC, abstractmethod 

@dataclass
class Transformation(ABC):
    target_traces: list[TimeTrace] # set of time traces you want to apply transform to 

    # optional additional parameters 
    


    def apply(self) -> TimeTrace:
        """
        here you implement the function that takes in a trace, applies a transform, then returns the modified version of the trace. 
        """
        
```
Example transformations could be filters, etc. 
```python
from dataclasses import dataclass
from src.data_processing.transformation import Transformation
@dataclass
class KaiserBesselFilter(Transformation):
    cuttoff_frequency: float 
    def apply(self):
        """
        apply the Kaiser-Bessel Filter and create a filtered version of the TimeTrace you passed in. 
        """

@dataclass
class MovingAverageFilter(Transformation):
    window_size: int 
    def apply(self):
        """
        apply the moving average and create a filtered version of the TimeTrace you passed in. 
        """
@dataclass
class ShiftToOrigin(Transformation):
    def apply(self):
        """
        set trace to start from the origin (as we do for synchronizing traces)
        """
```

<span style="color:lightgreen"> **NOTE: Transformations specific to particular assays/projects, such as the way bead heights get converted into nucleotide positions, will be implemented in their respective dedicated repositories** </span>

Now, we use a `ExperimentProcessor` that is responsible for keeping track of the `transformations` you want to perform to your `Experiment`

```python
@dataclass
class ExperimentProcessor:
    """
    ExperimentProcessor class keeps track of the set of Transformations to perform, applying the transforms is delayed until an explicit call to `transform_traces()`
    this way you can change your workflow by undoing/redoing transforms as many times as you want (as it under the hood just reproduces the series of events starting from the initial state)
    """

    experiment: Experiment
    transformations: list[Transformation] 
    state_index: int = 0

    def register(self, transformation: Transformation) -> None:
        """
        register the transformation.
        NOTE: If you undid a transformation (without redoing it), you will at this point 'confirm you actually never wanted to perform that operation'. After registering, we
        assume you want to point to the latest transformation.
        """

    def undo(self) -> None:
        """
        simply move pointer back by one (unless you are already pointing to the first Transformation)
        """

    def redo(self) -> None:
        """
        simply move pointer forward by one (unless there you are already pointing to the last Transformation)
        """

    def transform_traces(self) -> None:
        """
        Only when you call this function will things actually be computed.
        You compute it up until the state index
        """
        for transformation in self.transformations[: self.state_index]:
            transformation.apply()
```