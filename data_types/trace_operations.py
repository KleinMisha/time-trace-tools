"""
basic operations that allow us to add, subtract, etc. multiple traces.
Also includes shifting a trace to the left/right
"""

from typing import Dict, List

import numpy as np

from .trace import Trace


def add(trace_1: Trace, trace_2: Trace) -> Trace:
    """
    determine new Trace with positions added together
    """

    return Trace(
        x=trace_1.x + trace_2.x,
        y=trace_1.y + trace_2.y,
        z=trace_1.z + trace_2.z,
        t=trace_1.t,
        id="+".join([trace_1.id, trace_2.id]),
        is_REF_bead=False,
    )


def subtract(trace_1: Trace, trace_2: Trace) -> Trace:
    """
    determine new Trace with positions added together
    """

    return Trace(
        x=trace_1.x - trace_2.x,
        y=trace_1.y - trace_2.y,
        z=trace_1.z - trace_2.z,
        t=trace_1.t,
        id="-".join([trace_1.id, trace_2.id]),
        is_REF_bead=False,
    )


def average(trace_list: List[Trace]) -> Trace:
    """
    average bead postion of a list of traces
    """
    # add everything together
    for i, current_trace in enumerate(trace_list):
        if i == 0:
            trace_sum = trace_list[i]
        else:
            trace_sum = add(trace_sum, current_trace)

    # divide by the total number of traces used
    nmbr_traces = len(trace_list)
    avg_x = trace_sum.x / nmbr_traces
    avg_y = trace_sum.y / nmbr_traces
    avg_z = trace_sum.z / nmbr_traces
    return Trace(
        x=avg_x,
        y=avg_y,
        z=avg_z,
        t=trace_list[0].t,
        id=f"averaged {",".join([trace.id for trace in trace_list])}",
        is_REF_bead=False,
    )
