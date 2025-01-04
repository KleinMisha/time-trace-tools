"""
Core class to define an experiment (containing a series of traces)

"""

from typing import Any, List, Dict, Tuple
from .trace import Trace
from data_io.raw_mt import read_mt_data


class Experiment:
    """
    Experiment contains a set of Traces
    """

    def __init__(self, path: str, name: str, ref_bead: int = None) -> None:
        self.id = name
        self.ref_bead = ref_bead

        # instantiate the set of traces (includes loading data + subtracting reference bead)
        self.traces: List[Trace]

        # instantiate dictionaries to be populated during analysis
        self.sections: Dict[str, tuple[int, int, str]] = {}
        self.labels: Dict[str, Tuple[int, int]] = {}

    def _create_traces(self, path: str) -> None:
        """
        creates the Trace objects based on the raw data.
        Will deal with subtracting the signal of the raw data
        """
        # load the raw data
        beads_xyz, time = read_mt_data(path)
        (nmbr_beads, nmbr_frames, nmbr_channels) = beads_xyz.shape

        # create Trace() objects
        for nr in range(nmbr_beads):
            self.traces.append(
                Trace(
                    x=beads_xyz[nr, :, 0],
                    y=beads_xyz[nr, :, 1],
                    z=beads_xyz[nr, :, 2],
                    t=time,
                    id=nr,
                    is_REF_bead=(nr == self.ref_bead),
                )
            )

        # subtract the reference bead

        pass
