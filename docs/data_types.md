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
    ```

### Convenience methods 

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
