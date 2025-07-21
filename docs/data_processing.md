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
        Generic operation that adjust time traces, e.g. filtering, translation/rotation, subsection/selecting part of the trace, etc.
        """

        def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
            """
            apply transformation on the target traces to produce new set of traces
            """
            ...
    ```


???- Question "Why work with classes and not simply define a function?" 

    Different `Transformation` methods require their own set of parameters. While a method to select traces based on a label needs a string label as input, a method to filter traces probably needs some cutoff frequency. The Python syntax for defining a particular type of function (using the `Callable` type) is too limited to account for this in a clean way. Hence the class. 

    ---------
    Don't worry! Just make your function that applies an operation to an individual trace as you would normally do and then wrap `.apply()` around this function. Or use the `BaseTransformation` as detailed below to make this process easier. 

### Build your own Transformation 
Need to include an operation into your pipeline that is not yet build in? 
`TimeTraceTools` has a set of convenient base classes you can use to avoid worrying about implementing some common logic. Namely, the `BaseTransformation` has already implemented: 

1. **loop over the traces in your experiment**: Just worry about implementing `.apply_to_one_trace()` as the `.apply()` method already takes care of the tedious stuff. 
2. **pass-through:** When an operation is to operate only on a set of target traces, pass the other traces into the output in their unedited form. 
3. **validation:** Operations that should act on a particular axis (say filtering or translating the time trace) validate the existence of the given name of this value array. 

For convenience sake, we defined some easy 'presets' as well.

???- note "Wait! does this not introduce some nasty chain of inheritance, aka. code that is heavily coupled?"

    The trick is that ***no actual logic*** is implemented in these 'sub base types', they just narrow the scope of some argument types. 
    This type of 'shallow inheritance' does not actually complicate the logic/make code coupled in a bad way in my opinion. In fact, you can always use `BaseTransformation` as the parent directly. 

=== "BaseTransformation" 

    ```python linenums="1" title="Just worry about transforming an individual trace."
    
    from abc import ABC, abstractmethod
    class BaseTransformation(ABC):
        @abstractmethod
        def apply_to_one_trace():
            ...

        def apply():
            ...
    ```

=== "CoordinateTransformation"

    ```python linenums="1" title="Operations acting on a specific value array / coordinate"

    @dataclass 
    def CoordinateTransformation(BaseTransformation):

        coordinate: str 
        target_traces: Optional[list[str]]

    ```


=== "PassThroughTransformation"

    ```python linenums="1" title="A targeted operation. Keep the non-targets unedited."

    @dataclass 
    def PassThroughTransformation(BaseTransformation):
 
        target_traces: list[str]
        
    ```


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

=== "SelectTimeWindow"

    ```python linenums="1" title="cut out a specific time-span from the target traces."
    @dataclass
    class SelectTimeWindow:
        """
        Cut out a part of the trace starting/ending at the specified time points
        """

        target_traces: list[str]
        start_time: float
        end_time: float

        def generate_target_frames(
            self, time_array: NDArray[np.floating]
        ) -> tuple[int, int]:
            """Find nearest frames to specified time points"""
            start_frame = int(np.abs(time_array - self.start_time).argmin())
            end_frame = int(np.abs(time_array - self.end_time).argmin())
            return start_frame, end_frame

        def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
            """
            Call the SelectFrames Transformation
            """
            common_time_array = trace_list[0].t
            start_frame, end_frame = self.generate_target_frames(common_time_array)
            return SelectFrames(self.target_traces, start_frame, end_frame).apply(
                trace_list
            )
    ```

=== "ShiftToOrigin"

    ```python linenums="1" title="make the output time trace start at value 0 at time 0"

    @dataclass
    class ShiftToOrigin:
        """
        shift target traces to the origin (such that they start at value 0 at time 0)
        !Make sure to unit test that it does not modify the original traces. Should be fine given a deepcopy is passed into this from the ExperimentProcessor
        """

        target_traces: list[str]
        coordinate: str  # should match one of the available ._value_names of the TimeTrace class (e.g. MagneticTweezersTrace has 'x','y','z')

        def _traces_have_coordinate(
            self, trace_list: list[TimeTraceType]
        ) -> tuple[bool, Optional[str]]:
            """check if the coordinate is valid for the given target traces. If not, it will return the first trace ID at which the check fails"""
            targets = [trace for trace in trace_list if trace.ID in self.target_traces]
            for target_trace in targets:
                if self.coordinate not in target_trace._value_names:
                    return False, target_trace.ID

            return True, None

        def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
            """time-shift the trace along specified coordinate"""

            # quick check you have the coordinate available
            valid_coordinate, invalid_trace = self._traces_have_coordinate(trace_list)
            if not valid_coordinate:
                raise AttributeError(
                    f"Trace {invalid_trace} does not have a value-array named {self.coordinate}"
                )

            # the actual operation:
            new_traces = []
            for trace in trace_list:
                if trace.ID in self.target_traces:
                    time_array = trace.t
                    start_time = trace.t[0]
                    time_array -= start_time
                    value_array = trace.__getattribute__(self.coordinate)
                    starting_value = value_array[0]
                    value_array -= starting_value

                    shifted_trace = deepcopy(trace)
                    shifted_trace.__setattr__("t", time_array)
                    shifted_trace.__setattr__(self.coordinate, value_array)
                    new_traces.append(shifted_trace)

                else:
                    # keep the other traces unaffected.
                    new_traces.append(trace)
            return new_traces


    ```



### Filtering 
The `data_processing.filters` module contains some commonly used filtering schemes. 

=== "Filter abstraction"

    ```python linenums="1" title="Abstraction that implements some logic common to any type of filter to avoid code duplication."

    @dataclass 
    def Filter(BaseTransformation):

        @abstractmethod
        def filter():
            ... 

        def apply_to_one_trace():
            """ some of the stuff you would always need for any kind of filter is pre-implemented (and tested) for you"""

    ```

=== "Kaiser-Bessel"

    ```python linenums="1" title="Filter used in primer-extension traces"
    
    @dataclass
    def KaiserBesselFilter(Filter):

        cutoff_frequency: float 
        attenuation_dB: float 

        def filter():
            ...
    
    
    ```

=== "Moving average"

    ```python linenums="1" title="Simple sliding window averaging"
    
    @dataclass
    def MovingAverageFilter(Filter):

        window_size: float 

        def filter():
            ...
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

    The `ground truth` of the application is the list of transformations to be applied (and the state index indicating which ones have been applied). Note that the actual state of the time traces / experiment therefor is not. The transformed experiment is kept merely as a cached value for easy access after applying all transformations. 

    The reason for this choice is that this makes `.undo()` and `.redo()` much simpler to implement. Namely, instead of actually implementing the reverse operation of a `Transformation`, you just move the state index back by one and re-apply all transformations until the new index. 

    When saving your pipeline, you will not save the final state of the traces (at least, by default). In stead, a `TOML` file is created containing all information needed to recreate all `Transformation` instances / recreate the `ExperimentProcessor` that can simply apply all transformations again. 

    If Transformations take allot of time, consider storing an intermediate `Experiment` by itself. When reloading data, start an `ExperimentProcessor` using this intermediate as the new starting state. 


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
