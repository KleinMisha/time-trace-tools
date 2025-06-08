"""
Writing `Experiment`, and `TimeTrace` info to files


todo: write labels / section labels to files
todo:
"""

from pathlib import Path
from typing import Mapping

import numpy as np
from numpy.lib.npyio import NpzFile
from numpy.typing import NDArray

from data_types.time_trace import TimeTrace

FilePath = str | Path


def write_time_trace_values(time_traces: list[TimeTrace], path: FilePath) -> None:
    """
    Store the value arrays into a '.npz' file. The output file will contain time arrays +  named value arrays, names are taken from the first TimeTrace in the supplied list.
    also stores the names itself (easier reading from this file)
    NOTE: It is assumed all time traces are of the same subtype/concrete implementation.
    """

    # fetch names from the first trace (as we assume all traces are of the same kind)
    names = time_traces[0]._value_names

    # collect time arrays into one object
    time_arrays = [trace.t for trace in time_traces]

    # collect the value arrays from the traces (say: [(x1,y1,z2), (x2,y2,z2), ...])
    value_arrays = []
    for trace in time_traces:
        value_arrays.append(trace._values)

    # prepare saving to file by creating ({})
    value_data = {
        name: np.array(array, dtype=object)
        for name, array in zip(names, zip(*value_arrays))
    }

    np.savez(
        file=path, allow_pickle=True, t=time_arrays, **value_data, names=np.array(names)
    )


def read_time_trace_values(
    path: FilePath,
) -> tuple[NDArray[np.floating], dict[str, NDArray[np.floating]]]:
    """
    Read the npz file created above.
    Returns:
        1. Time arrays NDArray['t array for trace 1', 't array for trace 2', ...]
        2. named value arrays are stored into dictionary {
            name_value_1: NDArray[array for trace 1, array for trace 2, ...] ,
            name_value_2: NDArray[array for trace 2, array for trace 2, ...],
            ...
        }

    NOTE: Do not create `TimeTrace` objects here, let `TimeTrace` be responsible for that. This function is only responsible for reading/parsing the file created above
    """
    # used type hint here to indicate the format of NumPy's return from the load function (docstring says it returns 'Any', but we know the return type)
    loaded_data: Mapping[str, NDArray[np.floating]] = np.load(path, allow_pickle=True)
    t = loaded_data["t"]
    value_names = tuple([str(name) for name in loaded_data["names"]])
    value_arrays = {name: loaded_data[name] for name in value_names}
    return t, value_arrays
