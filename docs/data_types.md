# Internal data representation: `data_types` 

The `data_types` package offers convenient data representation to facilitate handling experimental data.

##  `TimeTrace` 
Fundamentally, single-molecule experiments will produce time-trajectories, or time traces. Using some convenient abstraction, a generic `TimeTrace` is defined to have some time-array, and any number of named value arrays of the same length. See the second tab for the specific implementation valid for traces of magnetic tweezers. 

=== "Abstraction" 

    ```python linenums="1" hl_lines="13-14 18 26" title="A generic time trace has some identifier/name and a time-array. "
    from abc import ABC, abstractmethod
    from dataclasses import dataclasses 
    from numpy.typing import NDArray 
    import numpy as np 

    class TimeTrace(ABC):
        """ A time trace at least has an identifier, a time-array, and at least one named value array"""
        ID: str
        t: NDArray[np.floating]

        @property
        @abstractmethod
        def _values(self) -> tuple[NDArray[np.floating], ...]:
            """
            return all the value arrays as a tuple.
            See subclasses for specific implementation
            """

        @property
        @abstractmethod
        def _value_names(self) -> tuple[str, ...]:
            """
            return a tuple of the names of the values. Should be same as the variable names
            used to instantiate class instance.
            """
    ```

=== "magnetic tweezers" 

    ```python linenums="1" hl_lines="11-13 20 24" title="magnetic tweezers have x,y,z coordinates as their value arrays"
    
    from dataclasses import dataclass, field

    import numpy as np
    from numpy.typing import NDArray

    from src.data_types.time_trace import TimeTrace


    @dataclass(eq=False)
    class MagneticTweezersTrace(TimeTrace):
        x: NDArray[np.floating] = field(default_factory=lambda: np.array([]))
        y: NDArray[np.floating] = field(default_factory=lambda: np.array([]))
        z: NDArray[np.floating] = field(default_factory=lambda: np.array([]))


        @property
        def _values(
            self,
        ) -> tuple[NDArray[np.floating], NDArray[np.floating], NDArray[np.floating]]:
            return (self.x, self.y, self.z)

        @property
        def _value_names(self) -> tuple[str, ...]:
            return ("x", "y", "z")
    ``` 

Hence, when dealing with data from the magnetic-tweezers instances of `MagneticTweezersTrace` will be created. 

```python linenums="1" title="Create a time trace" 
from src.data_types.magnetic_tweezers_trace import MagneticTweezersTrace 

mt_trace = MagneticTweezersTrace(
    ID = "trace_1",
    t = np.array([...]),
    x = np.array([...])
    y = np.array([...])
    z = np.array([...])
     )
```

### Qualitative labels 
In addition to an identifier and a time-array, a generic `TimeTrace` may be assigned any number of (qualitative) labels.
The same principle can be applied by assigning labels not to the entire trace, but to a particular section identified by the time frames / indices this section starts/stops at. 

```python linenums="1" 
    from abc import ABC, abstractmethod
    from dataclasses import dataclasses 
    from numpy.typing import NDArray 
    import numpy as np 

    class TimeTrace(ABC):
        """ A time trace at least has an identifier, a time-array, and at least one named value array"""
        ID: str
        t: NDArray[np.floating]
        labels: list[str] = field(default_factory=list)
        section_labels: dict[tuple[int, int], list[str]] = field(default_factory=dict)
```
For example, if a trace shows the signature of enzymatic activity

=== "full trace"

    ```python linenums="1" title="assign to labels"

    # convenience method to append to the list 
    my_trace.add_labels(["activity"])
    ```

=== "part of trace"

    ```python linenums="1" title="assign to section_labels"

    # convenience method to append to the list 
    my_trace.add_labelled_section(start_index=10000, end_index=20000, label="activity")
    ```

=== "assign from dictionary" 

    ```python linenums="1" title="batch assignment to section_labels"

    my_labels = {
        (0,5000): ["open hairpin"],
        (10000,20000): ["activity"],
    }

    my_trace.add_labelled_sections_from_dictionary(section_labels=my_labels)
    ```

### Convenience methods 
A number of convenience methods for adding/removing labels or retrieving a trace based on a particular section's label are available. 

#### Arithmetic and Comparison
Custom implementations of the addition, subtraction, division, and multiplication methods enable simple operations on all the values in a trace. Adding together two traces (or subtracting one trace from another) will result in a new `TimeTrace` with the same `t` array and the arithmetic applied to the value arrays. Additionally, simple syntax is enabled for basic arithmetic involving a scalar number.

=== "Addition"

    ```python linenums="1" hl_lines="2 5 8"

    # Add together two time traces by keeping the time array the same and having values equal to the sum of the individual traces 
    new_trace = trace_1 + trace_2 

    # Add a constant to all value arrays. Again leaving the time array intact (works with float and int)
    new_trace = trace_1 + 10. 

    # overwrite the current trace 
    trace_1  += 10. 
    ```

=== "Subtraction"

    ```python linenums="1" hl_lines="2 5 8"
    # Subtract a time trace from another by keeping the time array the same and having values equal to the difference of the individual traces  
    new_trace = trace_1 - trace_2 

    # Subtract a constant to all value arrays. Again leaving the time array intact (works with float and int)
    new_trace = trace_1 - 10. 

    # overwrite the current trace 
    trace_1  -= 10. 
    ```

=== "Multiplication"

    ```python linenums="1" hl_lines="2 5"
    # Multiply all values by a constant (works with float and int)
    new_trace = trace_1 * 10. 

    # overwrite the current trace 
    trace_1  *= 10. 
    ```
=== "Division"

    ```python linenums="1" hl_lines="2 5"
    # Multiply all values by a constant (works with float and int)
    new_trace = trace_1 / 10. 

    # overwrite the current trace 
    trace_1  /= 10. 
    ```

Additionally, the comparison operator (`==`) will check for equality on the elements of the value arrays
```python linenums="1" hl_lines="21 30 36-39" title="Equality checks"

from src.data_types.magnetic_tweezers_trace import MagneticTweezersTrace 

trace_1 = MagneticTweezersTrace(
    ID = "trace_1",
    t = np.array([0.,1.,2.,3.]),
    x = np.array([42.,42.,42.])
    y = np.array([42.,42.,42.])
    z = np.array([42.,42.,42.])
     )

trace_2 = MagneticTweezersTrace(
    ID = "trace_2",
    t = np.array([0.,1.,2.,3.]),
    x = np.array([42.,42.,42.])
    y = np.array([42.,42.,42.])
    z = np.array([42.,42.,42.])
     )

trace_3 = MagneticTweezersTrace(
    ID = "trace_3",
    t = np.array([0.,10.,20.,30.]),
    x = np.array([42.,42.,42.])
    y = np.array([42.,42.,42.])
    z = np.array([42.,42.,42.])
     )

trace_4 = MagneticTweezersTrace(
    ID = "trace_4",
    t = np.array([0.,1.,2.,3.]),
    x = np.array([0.,4.,2.])
    y = np.array([42.,42.,42.])
    z = np.array([42.,42.,42.])
     )


# trace_1 and trace_2 are equal, all others are not 
trace_1 == trace_2 # True 
trace_1 == trace_3 # False: different time array  
trace_1 == trace_4 # False: different value array
```


## `Experiment` 
An `Experiment` is our go-to container for a set of `TimeTrace` objects 

=== "Abstraction"

    ```python linenums="1" hl_lines="26-28 32" title="from experiment.py"
    from abc import ABC, abstractmethod
    from dataclasses import dataclass, field
    from pathlib import Path
    from typing import Any, Callable, Generic

    from numpy.typing import NDArray
    import numpy as np 

    from src.data_types.time_trace import TimeTrace
    from src.data_types.type_definitions import TimeTraceType

    FilePath = Path | str
    DataLoaderFunction = Callable[[FilePath], tuple[NDArray[Any], ...]]


    @dataclass
    class Experiment(ABC, Generic[TimeTraceType]):
        """
        Defines a generic experiment as a container of TimeTrace instances.
        Generally speaking an experiment has a name, and a set of time traces that are loaded
        from a raw data file.
        Additionally, experimental conditions can be added as a dictionary to keep track of additional metadata.

        """

        ID: str
        traces: list[TimeTraceType] = field(default_factory=list)
        path_to_raw_data: FilePath = Path("")
        experimental_conditions: dict[str, Any] = field(default_factory=dict)

        @abstractmethod
        def _create_trace_list_from_raw_data(self) -> list[TimeTraceType]:
            """
            Implement how the traces should be instantiated based on the loaded raw data
            As data from different experiments might have different structures, intentionally left this as abstract method
            """
            pass
    ```

=== "magnetic tweezers"

    ```python linenums="1" hl_lines="9-26" title="from magnetic_tweezers_experiment.py"    
    
    from src.data_types.experiment import Experiment
    from src.data_types.magnetic_tweezers_trace import MagneticTweezersTrace


    @dataclass
    class MagneticTweezersExperiment(Experiment[MagneticTweezersTrace]):

        def _create_trace_list_from_raw_data(self) -> list[MagneticTweezersTrace]:
            """
            create the instances of the MagneticTweezersTrace based on the loaded raw data

            Make some standard identifiers
            """
            trace_list = []
            bead_positions_xyz: NDArray  # Now Pylance understands .shape is a thing
            bead_positions_xyz, time = self._raw_data
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
    ```

### Convenience methods 
Includes methods for 

* **retrieving traces** by their identifiers and/or labels. 
* **adding / removing traces** from the current experiment 
* **assigning a common set of (section) labels** to all traces within an experiment 


### Arithmetic 
The basic addition and subtraction operators have been overloaded to easily merge two experiments together 

=== "Addition"
    ```python linenums="1" title="Create a new experiment with all traces of experiments 1 and experiment 2"

    merged_experiment = exp_1 + exp_2 
    ```

=== "Subtraction"
    ```python linenums="1" title="Exclude all the traces belonging to experiment 2"

    # the same as `exp_1` in this case ;-) 
    exclude_exp_2 = merged_experiment - exp_2 
    ```

The same goes for adding/excluding individual `TimeTrace` instances from the `Experiment`.

=== "Addition"
    ```python linenums="1" title="Include an additional trace"

    # To explain what is going on ... 
    from src.data_types.type_definitions import TimeTraceType, ExperimentType 

    additional_trace: TimeTraceType 
    experiment: ExperimentType  

    # .. in this one line of actual code you need to write. 
    one_more_trace = experiment + additional_trace 
    ```

=== "Subtraction"
    ```python linenums="1" title="Exclude a particular trace"
    # To explain what is going on ... 
    from src.data_types.type_definitions import TimeTraceType, ExperimentType 

    ugly_trace: TimeTraceType 
    experiment: ExperimentType  

    # .. in this one line of actual code you need to write. 
    excl_ugly_trace = experiment - ugly_trace 
    ```
