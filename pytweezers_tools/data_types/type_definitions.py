"""
Move all the type definitions into here for the following reasons:

1. Avoids rewriting these lines of code at the top of every file (just import this)
2. Avoids circular imports for trace_operations.py
    --> trace_operations.py imports TimeTraceType from time_trace (just for the type hint )
    --> time_trace.py imports trace_operations...
    ---> leads to circular imports (error)

Using this separate file should avoid these issues (according to chatGPT)


"""

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from experiment import Experiment
    from time_trace import TimeTrace

TimeTraceType = TypeVar("TimeTraceType", bound="TimeTrace")
ExperimentType = TypeVar("ExperimentType", bound="Experiment")
