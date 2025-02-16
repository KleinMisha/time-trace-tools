from dataclasses import dataclass
from typing import Any, Optional

from .experiment_series import ExperimentSeries
from .magnetic_tweezers_experiment import MagneticTweezersExperiment


@dataclass
class MagneticTweezersExperimentSeries(ExperimentSeries[MagneticTweezersExperiment]):
    def create_experiments(
        self,
        filepaths: Optional[list[str]],
        variable_condition: Optional[dict[str, float | int]],
        common_conditions: Optional[dict[str, Any]],
        ref_bead_nrs: list[int] = [],
    ) -> None:
        return super().create_experiments()
