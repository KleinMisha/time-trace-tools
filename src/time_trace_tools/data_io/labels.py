"""
Extremely simple readers/writers for dictionaries of labels and section labels
"""

import json
from pathlib import Path
from typing import Any, TypedDict

from time_trace_tools.data_types.experiment import Experiment

FilePath = Path | str


# convenient type definitions for JSON data
class SectionJSON(TypedDict):
    start: int
    end: int
    labels: list[str]


SectionJSONObject = dict[str, list[SectionJSON]]


def write_experiment_labels(experiment: Experiment, path: FilePath) -> None:
    experiment_labels = experiment.get_labels()
    with open(path, "w") as f:
        json.dump(experiment_labels, f)


def write_experiment_section_labels(experiment: Experiment, path: FilePath) -> None:
    experiment_section_labels = experiment.get_section_labels()
    sections_json = _serialize_section_labels(experiment_section_labels)

    with open(path, "w") as f:
        json.dump(sections_json, f)


def read_json(path: FilePath) -> dict[str, Any]:
    with open(path, "r") as f:
        data = json.load(f)
    return data


def _serialize_section_labels(
    section_labels: dict[str, dict[tuple[int, int], list[str]]],
) -> SectionJSONObject:
    """
    Format the section labels such that they can actually be written to a file properly.
    ---
    JSON cannot have the inner dictionary with the tuple as a key
    """
    return {
        ID: [
            {"start": start, "end": end, "labels": labels}
            for (start, end), labels in trace_sections.items()
        ]
        for ID, trace_sections in section_labels.items()
    }
