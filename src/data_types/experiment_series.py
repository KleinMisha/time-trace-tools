from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from .experiment import ExperimentType

ExperimentSeriesType = TypeVar("ExperimentSeriesType", bound="ExperimentSeries")


@dataclass
class ExperimentSeries(ABC, Generic[ExperimentType]):
    """
    Defines a generic experiment series as a container of Experiment instances.
    """

    ID: str
    experiments: list[ExperimentType] = field(default_factory=list)
    dependent_variable: str = ""

    @abstractmethod
    def create_experiments(self) -> None:
        """
        Supply lists of:
        - experiment IDs
        - optional list of (raw) data files
        - optional set of experimental conditions (use `_create_dicts_for_condition_sweep()` for convenience)
        - additional parameters/attributes used to instantiate the experiment
        """
        pass

    def _create_dicts_for_condition_sweep(
        self,
        variable_condition: dict[str, list[float | int]],
        common_conditions: dict[str, Any] = {},
    ) -> list[dict[str, Any]]:
        """
        use the resulting dictionaries to create instances of Experiment
        """

        VARIED_CONDITION = list(variable_condition.keys())[0]
        COMMON = common_conditions.copy()
        condition_list = []
        for value in variable_condition[VARIED_CONDITION]:
            condition_list.append(COMMON.update({VARIED_CONDITION: value}))
        return condition_list

    def add_experiments(self, experiment_list: list[ExperimentType]) -> None:
        self.experiments.extend(experiment_list)

    def remove_experiment(self, experiment_id: str) -> None:
        after_removal = [
            experiment
            for experiment in self.experiments
            if experiment.ID != experiment_id
        ]
        self.experiments = after_removal

    def fetch_experiment(self, experiment_id: str) -> ExperimentType:
        for experiment in self.experiments:
            if experiment.ID == experiment_id:
                return experiment
        raise KeyError(
            f"ExperimentSeries does not contain Experiment with ID {experiment_id}"
        )

    def __len__(self) -> int:
        return len(self.experiments)
