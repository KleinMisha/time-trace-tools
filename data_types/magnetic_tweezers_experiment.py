from dataclasses import dataclass
from typing import Optional

import numpy as np

from .experiment import Experiment
from .magnetic_tweezers_trace import MagneticTweezersTrace


@dataclass
class MagneticTweezersExperiment(Experiment[MagneticTweezersTrace]):
    ref_bead_nr: int = 1
    ref_bead_id: str = "bead_1"

    @property
    def REF_beads(self) -> list[MagneticTweezersTrace]:
        return [trace for trace in self.traces if trace.is_REF]

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

    def set_reference_bead(
        self, ref_bread_id: str, keep_previous_ref: bool = False
    ) -> None:
        """
        Switch between reference beads, or register another bead as being a reference bead.


        TODO: Now the reference bead will be placed at the end. Maybe adjust this to make it possible to place it back at its original location in the list of traces
        """
        new_ref_bead = self.fetch_trace(trace_id=ref_bread_id)
        new_ref_bead.is_REF = True
        # replace the original with the new one that is now set as reference trace
        self.remove_trace(trace_id=ref_bread_id)
        self.add_traces(trace_list=[new_ref_bead])

        # find and remove old reference beads
        old_ref_beads = self.REF_beads
        for trace in old_ref_beads:
            trace.is_REF = False
            self.remove_trace(trace_id=trace.ID)
        self.add_traces(trace_list=old_ref_beads)

        if not keep_previous_ref:
            for trace in self.traces:
                if trace.is_REF:
                    trace.is_REF = False
                    self.remove_trace(trace_id=trace.ID)
                    self.add_traces(trace_list=[trace])

    def subtract_reference_bead(self, ref_bead_nr: Optional[int]) -> None:
        raise NotImplementedError
