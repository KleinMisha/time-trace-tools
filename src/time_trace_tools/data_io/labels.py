"""
Extremely simple readers/writers for dictionaries of labels and section labels
"""

import json
from pathlib import Path
from typing import Any

from time_trace_tools.data_types.experiment import Experiment

FilePath = Path | str


def write_experiment_labels(experiment: Experiment, path: FilePath) -> None:
    experiment_labels = experiment.get_labels()
    with open(path, "w") as f:
        json.dump(experiment_labels, f)


def write_experiment_section_labels(experiment: Experiment, path: FilePath) -> None:
    experiment_section_labels = experiment.get_section_labels()
    with open(path, "w") as f:
        json.dump(experiment_section_labels, f)


def read_json(path: FilePath) -> dict[str, Any]:
    with open(path, "r") as f:
        data = json.load(f)
    return data
