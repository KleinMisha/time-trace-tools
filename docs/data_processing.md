# Flexible and simplified data postprocessing: `data_processing` 
The `data_processing` package offers convenient tools to analyze and post-process your `Experiment` data. 

## `Transformation` 
To define a general purpose handler of any workflow, we define a `Transformation` as any operation that 

1. acts on a specified set of target traces 
2. produces a new list of `TimeTraces`s from the original one. 

=== "Class" 
    Most (pre-)/(post-)processing manipulations can be summarized as creating a mutated form of a list of traces by applying a method to a set of target traces. 

    ```mermaid
    classDiagram 
        class Transformation{
        +list[str]: target_traces
        ... 

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

        # trace identifiers you want to modify
        target_traces: list[str]

        def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
            """
            apply transformation on the target traces to produce new set of traces
            """
            ...
    ```


???- Question "Why work with classes and not simply define a function?" 

    Different `Transformation` methods require their own set of parameters. While a method to select traces based on a label needs a string label as input, a method to filter traces probably needs some cutoff frequency. The Python syntax for defining a particular type of function (using the `Callable` type) is too limited to account for this in a clean way. Hence the class. 

    ---------
    Don't worry! Just make your function that applies an operation to an individual trace as you would normally do and then wrap `.apply()` around this function. 

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


## `ExperimentProcessor` 




