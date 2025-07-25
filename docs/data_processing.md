# Flexible and simplified data postprocessing: `data_processing` 
The `data_processing` package offers convenient tools to analyze and post-process your `Experiment` data. 

## `Transformation` 
To define a general purpose handler of any workflow, we define a `Transformation` as any operation that acts on (a specified set of target) traces to produce a new list of `TimeTraces`s from the original one. 

=== "Class" 
    Most (pre-)/(post-)processing manipulations can be summarized as creating a mutated form of a list of traces by applying a method to a set of target traces. 

    ```mermaid
    classDiagram 
        class Transformation{
            
        PARAMETERS AS ATTRIBUTES

        +apply(trace_list:list[TimeTrace])*: list~TimeTrace~
        }
    ```

=== "Code" 

    ```python linenums="1" hl_lines="7 9" title="Protocol defines a 'transformation interface'."


    from typing import Protocol

    from src.data_types.type_definitions import TimeTraceType

    class Transformation(Protocol):
        """
        A Transformation is any operation that takes a list of TimeTrace objects and returns a new list of TimeTrace objects
        """

        def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]: ...

    ```


???- Question "Why work with classes and not simply define a function?" 

    Different `Transformation` methods require their own set of parameters. While a method to select traces based on a label needs a string label as input, a method to filter traces probably needs some cutoff frequency. The Python syntax for defining a particular type of function (using the `Callable` type) is too limited to account for this in a clean way. Hence the class. 

    ---------
    Don't worry! Just make your function that applies an operation to an individual trace as you would normally do and then wrap `.apply()` around this function. Or use the `BaseTransformation` as detailed below to make this process easier. 

### Build your own Transformation 
Need to include an operation into your pipeline that is not yet build in? 
`TimeTraceTools` has a set of convenient base classes you can use to avoid worrying about implementing some common logic. Namely, the `BaseTransformation` has already implemented: 

1. **loop over the traces in your experiment**: Just worry about implementing `.apply_to_one_trace()` as the `.apply()` method already takes care of the tedious stuff. 
2. **Check if a trace should be edited**: Targeted operations need to always perform a simple check to see if the trace exist in the list of desired targets. 
3. **pass-through:** When an operation is to operate only on a set of target traces, pass the other traces into the output in their unedited form. 
4. **validation:** Operations that should act on a particular axis (say filtering or translating the time trace) validate the existence of the given name of this value array. 



=== "BaseTransformation (class)" 


    ```mermaid
    classDiagram 
        class BaseTransformation{
            
        + list~str~ | None: target_traces
        + str | None: coordinate 

        +apply_to_one_trace(trace:TimeTrace)*: TimeTrace
        +apply(trace_list:list~TimeTrace~)*: list~TimeTrace~
        +_should_transform(trace:TimeTrace)*: bool
        +_validate_coordinate_exists(trace:TimeTrace)*: bool
        }
    ```

=== "BaseTransformation (code)" 

    ```python linenums="1" hl_lines="13-14 17-18 20 29 37-47" title="Just worry about transforming an individual trace."
    
    from abc import ABC, abstractmethod
    class BaseTransformation(ABC):
        """
        Abstract Base Class with optional shared logic.
        Simplifies testing shared logic as it is now localized.
        Also NOTE the subclasses defined below are 100% optional, and merely defined to make development of new Transformation implementations more convenient.
        Hence, this class prevents actual deep inheritance chains (unnecessary coupling).
        """

        def __init__(
            self, target_traces: Optional[list[str]], coordinate: Optional[str]
        ) -> None:
            self.target_traces = target_traces
            self.coordinate = coordinate

        @abstractmethod
        def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
            """Apply the transformation to an individual trace"""

        def _should_transform(self, trace: TimeTraceType) -> bool:
            """
            Checks if the supplied trace is a target of the Transformation.
            If target_traces is an empty list, you will apply the transform to all traces
            """
            if not self.target_traces:
                return True
            return trace.ID in self.target_traces

        def _validate_coordinate_exists(self, trace: TimeTraceType) -> None:
            """Check that the supplied coordinate is a valid name of a property of the time trace."""

            if self.coordinate and self.coordinate not in trace._value_names:
                raise AttributeError(
                    f"Trace {trace.ID} does not have a value-array named {self.coordinate}"
                )


        #.apply() already takes care of some typical shared logic to avoid duplicate code 
        def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
            new_traces = []
            for trace in trace_list:
                if self._should_transform(trace):
                    self._validate_coordinate_exists(trace)
                    new_traces.append(self.apply_to_one_trace(trace))
                else:
                    new_traces.append(trace)
            return new_traces
    ```

For convenience sake, we defined some easy 'presets' as well.



=== "CoordinateTransformation"

    ```python linenums="1" title="Operations acting on a specific value array / coordinate"

    @dataclass
    class CoordinateTransformation(BaseTransformation):
        """A Transformation that acts on a particular coordinate"""

        coordinate: str
        target_traces: Optional[list[str]]  # NOTE: redefine here to make type checker happy


    ```


=== "PassThroughTransformation"

    ```python linenums="1" title="A targeted operation. Keep the non-targets unedited."
    @dataclass
    class PassThroughTransformation(BaseTransformation):
        """
        Target traces are supplied + non-target traces get passed into the output unedited.
        Does not need the logic for coordinate-specific operations
        """

        coordinate: Optional[str]  # NOTE: redefine here to make type checker happy
        target_traces: Optional[list[str]]

        
    ```

=== "AllTracesTransformation"

    ```python linenums="1" title="Transformation that will act on all traces."
    @dataclass
    class AllTracesTransformation(BaseTransformation):
        """No defined target traces, simply works on the full list of traces supplied to the .apply() method"""

        coordinate: Optional[str]  # NOTE: redefine here to make type checker happy
        target_traces: None = None
    ```
=== "HasCoordinateAllTraces"

    ```python linenums="1" title="Acts on a specific value array of all traces."

    @dataclass
    class HasCoordinateAllTraces(BaseTransformation):
        """Needs a name of an existing value array, and explicitly operates on all input traces"""

        coordinate: str
        target_traces: None = None
    ```
???- note "Wait! does this not introduce some nasty chain of inheritance, aka. code that is heavily coupled?"

    The trick is that ***no actual logic*** is implemented in these 'sub base types', they just narrow the scope of some argument types. 
    This type of 'shallow inheritance' does not actually complicate the logic/make code coupled in a bad way in my opinion. In fact, you can always use `BaseTransformation` as the parent directly. 




### Basic transformations 
The `data_processing.common_transformations.py` module contains some basic selections and simple manipulations. Some examples 

=== "SelectTraces"

    ```python linenums="1" title="fetch traces by their IDs"
    @dataclass
    class SelectTraces:
        """keep only the traces with the desired identifiers"""

        target_traces: list[str]

        def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
            return [trace for trace in trace_list if trace.ID in self.target_traces]
    ```

=== "SelectByLabels"

    ```python linenums="1" title="select traces with a specific (set of) qualitative labels"
    @dataclass
    class SelectTracesByLabels:
        """only keep the traces with a specific (set of) label(s)"""

        target_traces: list[str]
        target_labels: list[str]

        def generate_trace_ids(self, trace_list: list[TimeTraceType]) -> list[str]:
            """helper function that defines the new target traces for the generic SelectTraces"""
            return [
                trace.ID
                for trace in trace_list
                if trace.ID in self.target_traces
                and set(trace.labels) == set(self.target_labels)
            ]

        def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
            selected_traces = self.generate_trace_ids(trace_list)
            return SelectTraces(selected_traces).apply(trace_list)
    ```

=== "SelectFrames"

    ```python linenums="1" title="cut out a specific set of frames (subset by index in the array)"
    @dataclass
    class SelectFrames(PassThroughTransformation):
        """
        Cut out a part of the target trace(s) starting/ending at the given frames (every time point in a time trace is one time frame)
        Inherit from `BaseTransformation` to get the passthrough logic: non-target traces get passed on to output
        """

        start_frame: int
        end_frame: int

        def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
            """create a new TimeTrace object containing only the data corresponding to the desired frames"""
            section_of_trace = trace.create_time_trace_for_section(
                start_index=self.start_frame, end_index=self.end_frame
            )
            return section_of_trace
    ```

=== "SelectTimeWindow"

    ```python linenums="1" title="Cut out a specific time-span from your traces"
    @dataclass
    class SelectTimeWindow(PassThroughTransformation):
        """
        Cut out a part of the trace starting/ending at the specified time points
        """

        start_time: float
        end_time: float

        def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
            """Similar logic as SelectFrames, now first need to get nearest frames to selected time points"""
            start_frame, end_frame = self._determine_nearest_frames(trace.t)
            section_of_trace = trace.create_time_trace_for_section(
                start_index=start_frame, end_index=end_frame
            )
            return section_of_trace

        def _determine_nearest_frames(
            self, time_array: NDArray[np.floating]
        ) -> tuple[int, int]:
            """Find nearest frames to specified time points"""
            start_frame = int(np.abs(time_array - self.start_time).argmin())
            end_frame = int(np.abs(time_array - self.end_time).argmin())
            return start_frame, end_frame
    ```

=== "ShiftToOrigin"

    ```python linenums="1" title="make the output time trace start at value 0 at time 0"
    @dataclass
    class ShiftToOrigin(CoordinateTransformation):
        """
        shift target traces to the origin (such that they start at value 0 at time 0)
        """

        def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
            """return new traces starting from value 0 at time 0"""
            time_array = trace.t
            start_time = trace.t[0]
            time_array -= start_time
            value_array = trace.__getattribute__(self.coordinate)
            starting_value = value_array[0]
            value_array -= starting_value

            shifted_trace = deepcopy(trace)
            shifted_trace.__setattr__("t", time_array)
            shifted_trace.__setattr__(self.coordinate, value_array)
            return shifted_trace
    ```



### Filtering 
The `data_processing.filters` module contains some commonly used filtering schemes. 

=== "Filter abstraction"

    ```python linenums="1" title="Abstraction that implements some logic common to any type of filter to avoid code duplication."

    @dataclass
    class Filter(CoordinateTransformation):
        """A generic Filter Transformation. Gather common functionality in here to avoid duplicate code/ allow for simple testing."""

        @abstractmethod
        def filter(
            self, time: NDArray[np.floating], raw_signal: NDArray[np.floating]
        ) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
            """Implement the specific filtering operation here. Return (time, filtered_signal)"""

        def apply_to_one_trace(self, trace: TimeTraceType) -> TimeTraceType:
            """creation of the filtered TimeTrace has shared logic independent of the actual filter operation"""
            
            # fetch the values you should filter 
            time = trace.t
            value_array = trace.__getattribute__(self.coordinate)

            # apply filtering method 
            filtered_time, filtered_values = self.filter(time, value_array)

            # return a TimeTrace with modified values 
            filtered_trace = trace
            filtered_trace.__setattr__("t", filtered_time)
            filtered_trace.__setattr__(self.coordinate, filtered_values)
            return filtered_trace

    ```

=== "Kaiser-Bessel"

    ```python linenums="1" title="Filter used in primer-extension traces"
    
    @dataclass
    class KaiserBesselFilter(Filter):
        """
        Kaiser-Bessel (low-pass) filter.
        ---
        Typical filter used for polymerase primer-extension traces.
        """

        acquisition_frequency: float = 58.0 # as used to record the data 
        cutoff_frequency: float = 2.0. # attenuate frequencies from this point onwards 
        transition_width: float = 0.01  # sets the sharpness of the transition between pass- and stop-bands. relative to nyquist frequency. So width in Hz = width * acquisition_frequency /2
        stopband_attenuation_dB: float = 100 # desired attenuation of frequencies much greater than the cutoff_frequency + transition_width. NOTE: Only approximately reaches this level. 

        def filter():
            """See data_processing.filters for implementation """
    
    ```

=== "Moving average"

    ```python linenums="1" title="Simple sliding window averaging"
    
    @dataclass
    class MovingAverageFiler(Filter):
        r"""
        Sliding window filter
        ---
        Time-domain impulse response:
        h[n] = 1/M for  0<=n<=M , 0 else

        Window size is calculated based on the desired time window and acquisition frequency as:
        M = T * f_acq

        Hence, the output signal y[n] is calculated from the input signal x[n] using
        y[n] = \frac{1}{M} \sum_{k=0}^{M-1} x[n-k]

        NOTE: To deal with the first M windows, the average is taken over the available points,
            effectively ramping up the size M at the beginning and scaling it down at the end.
        """

        time_window: float
        acquisition_frequency: float = 58.0

        def __post_init__(self):
            """Determine window size upon instantiation"""
            self._window_size = int(self.time_window * self.acquisition_frequency)
        
        def filter():
            """See data_processing.filters for implementation """
    ```

## `ExperimentProcessor` 
Use the `ExperimentProcessor` to execute your pipeline / apply (a series of) transformation(s). 
This class implements what is commonly referred to as 'the command design pattern', which is a clean way of allowing for complete flexibility for different transformation pipelines.
Specifically, the `ExperimentProcessor` takes care of: 

1. A list of `Transformation` instances to be applied. 
2. Applying the transformations 
3. Undoing a transformation
4. Redoing a transformation previously undone

???+ note "Transformations as the ground through, not the state of the experiment"

    The `ground truth` of the application is the list of transformations to be applied (and the state index indicating which ones have been applied). Note that the actual state of the time traces / experiment therefo is not. The transformed experiment is kept merely as a cached value for easy access after applying all transformations. 

    The reason for this choice is that this makes `.undo()` and `.redo()` much simpler to implement. Namely, instead of actually implementing the reverse operation of a `Transformation`, you just move the state index back by one and re-apply all transformations until the new index. 

    When saving your pipeline, you will not save the final state of the traces (at least, by default). In stead, a `TOML` file is created containing all information needed to recreate all `Transformation` instances / recreate the `ExperimentProcessor` that can simply apply all transformations again. 

    If Transformations take allot of time, consider storing an intermediate `Experiment` by itself. When reloading data, start an `ExperimentProcessor` using this intermediate as the new starting state. 


=== "Class"
    ```mermaid
    classDiagram 
        class ExperimentProcessor{
            
        + Experiment: original_experiment 
        + list~Transformation~: transformations 
        + int: state_index = 0. 
        + Experiment: _current_experiment

        +add_transformation(transformation: Transformation)
        +add_transformations(transformations: Iterable~Transformation~)
        + run()
        + undo()
        + redo()
        + get_current_experiment(): Experiment 
        + get_current_traces(): list~TimeTrace~

        }
    ```

=== "Code"

    ```python linenums="1" title="The Experiment processor"
    from src.data_processing.transformation import Transformation
    from src.data_types.experiment import Experiment

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
    ```


### Registering Transformations 
Setting up your `ExperimentProcessor` is done by 

1. Instantiating it from a given `Experiment` containing the traces that will be considered in their unedited/starting state. 
2. Register a `Transformation` using the `.add_transformation()` method. Or register your entire pipeline as a list of `Transformations` using the `add_transformations()` method. 
 
### Executing pipeline 
Applying all transformations is as easy as calling the `.run()` method.

```python linenums="1" title="Apply pipeline"    
processor.run()
```



### Undo/Redo 
Made a mistake? Undo/redo transformations as follows 

=== "Undo"

    ```python linenums="1" title="Undo the last transformation" 
    # exclude the final transformation 
    processor.undo() 

    # re-apply new pipeline to see effect 
    processor.run() 
    ```
=== "Redo"

    ```python linenums="1" title="Redo the excluded transformation" 
    # exclude the final transformation 
    processor.undo() 
    # re-apply new pipeline to see effect 
    processor.run() 

    # Actually, we need that final transformation anyways 
    processor.redo()
    # re-apply new pipeline to see effect 
    processor.run() 
    ```

???+ info "This is why we do not use the time traces as the ground truth"

    The power here lies in that we no longer need to worry of "how do I unfilter a trace? Ow wait, I want to filter them anyways, need to re-implement the filter..." Simply play around with some.

### Retrieve final result

When done applying your pipeline, you can check the final form of the `Experiment` stored as `._current_experiment`, which can be retrieved using: 

=== "Final Experiment"

    ```python linenums="1" title="Experiment object"

    final_experiment = processor.get_current_experiment()

    # This is the same as: 
    final_traces = processor._current_experiment 
    ```
=== "Directly get the list of traces"

    ```python linenums="1" title="Experiment object"

    final_traces = processor.get_current_traces()

    # This is the same as: 
    final_traces = processor._current_experiment.traces 
    ```
