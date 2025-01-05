from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from experiment import Experiment
from magnetic_tweezers_trace import MagneticTweezersTrace

from data_io.raw_mt import read_mt_data


@dataclass
class MagneticTweezersExperiment(Experiment):
    ref_bead_nr: int = 1
    ref_bead_id: str = "bead_1"

    def _create_trace_list_from_raw_data(self) -> list[MagneticTweezersTrace]:
        """
        create the instances of the MagneticTweezersTrace based on the loaded raw data

        Make some standard identifiers
        """
        trace_list = []
        bead_positions_xyz: np.ndarray  # Now Pylance understands .shape is a thing
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

    def subtract_reference_bead(self, ref_bead_nr: Optional[int]) -> None:
        raise NotImplementedError
