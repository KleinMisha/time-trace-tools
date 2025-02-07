"""
Reading/parsing the magnet script from PyTweezers
"""

import numpy as np
import pandas as pd

# some general imports
from pathlib import Path

FilePath = Path | str


def read_magnet_script_pytweezers(path: FilePath) -> pd.DataFrame:
    """
    magnet script is stored as a space separated text file.
    column headers are not included in the file.
    this function will parse the file to read

    step | duration_s | magnet_height_target | speed_mm_per_s | turns_target | rotation_rate_turns_per_s | comments

    """

    WITHOUT_COMMENTS = 5  # number columns without comments
    HEADERS = [
        "duration_s",
        "magnet_height_mm",
        "move_rate_mm_per_s",
        "magnet_rotation_turns",
        "rotation_rate_turns_per_s",
        "comments",
    ]
    table_content = []
    with open(path, "r") as file:
        for line in file.readlines():
            split_by_space = line.split()
            new_row = [float(val) for val in split_by_space[:WITHOUT_COMMENTS]] + [
                " ".join(split_by_space[WITHOUT_COMMENTS:])
            ]
            table_content.append(new_row)
    output_table = pd.DataFrame(table_content, columns=HEADERS)
    return output_table


def create_sections_from_file(
    path: FilePath,
    frame_rate_Hz: float,
) -> dict[tuple[int, int], list[str]]:
    """
    create dictionary with sections applicable to all traces of a given experiment
    use the read_magnet_script_pytweezers() function to generate input table
    """
    # load/parse the magnet script
    magnet_script_table = read_magnet_script_pytweezers(path)

    # get the start/stop times from the table
    end_times = list(np.cumsum(magnet_script_table["duration_s"]))
    start_times = [0.0] + end_times[:-1]

    # use frame rate to convert into index in time array
    start_indices = [round(frame_rate_Hz * time) for time in start_times]
    end_indices = [round(frame_rate_Hz * time) for time in end_times]

    # create dictionary
    # use 'comments' to name the sections
    section_labels = [comment for comment in magnet_script_table["comments"]]

    section_dictionary = {}
    for start_index, end_index, label in zip(
        start_indices, end_indices, section_labels
    ):
        new_entry = {(start_index, end_index): [label]}
        section_dictionary.update(new_entry)
    return section_dictionary
