"""
Convert raw data from PyTweezer to LabView's format to use older GUIs

-- Misha, October 2024
"""

import numpy as np
import pandas as pd


# LabView :: Older data is taken before we had pytweezers, but we still want to inspect things the same way
def read_labview(path: str) -> tuple[np.ndarray, np.ndarray]:
    """
    read raw data produced by LabView ('.txt')

    Args:
        path (str): absolute path to .txt file

    Returns:
        np.ndarray: An array with dimensions (num_beads, num_frames, 3). For every bead there is an array of (x,y,z) in the columns and frames in the rows
        np.ndarray: The time in seconds

    Notes:
        reads the original .txt as a table, renames the columns to more easily group together (x,y,z) of the same column
        NOTE: possibly could be done more efficient, but this is sufficient for now
    """

    # ---- load file ----
    data = pd.read_table(path, header=None, dtype="float32")

    # - every bead has three columns: x,y,z. First column is time in milliseconds.
    num_columns = len(data.columns)
    num_beads = (num_columns - 1) // 3
    num_frames = len(data)

    # --- drop the final column with NaNs and the first column with just the index ---
    data.drop(columns=data.columns[[0, -1]], inplace=True)

    # rename the columns in the data
    column_names = ["Time_ms"]
    for bead_nr in range(num_beads):
        for suffix in ["_x", "_y", "_z"]:
            column_names.append(f"Bead_{bead_nr + 1}" + suffix)
    rename_dict = {data.columns[i]: column_names[i] for i in range(len(column_names))}
    data.rename(mapper=rename_dict, axis="columns", inplace=True)

    # --- Build the output array:  allocate X,Y,Z data as 3D np.array ---
    beads_xyz = np.zeros((num_beads, num_frames, 3))
    for bead_nr in range(num_beads):
        cols = [f"Bead_{bead_nr + 1}_{ax}" for ax in ["x", "y", "z"]]
        one_bead = data[cols].values
        beads_xyz[bead_nr, :, :] = one_bead

    # -- time array ----
    # NOTE: `data["Time_ms"].values / 1000.0` totally works, but typechecker started to complaint about it, so opted for this more "pythonic" solution
    # NOTE: Should not be too much of a performance drop.
    t = np.array([t_ms / 1000.0 for t_ms in data["Time_ms"].values])
    return beads_xyz, t


def pytweezer_to_labview(
    pytweezers_xyz: np.ndarray, t: np.ndarray, path_out: str
) -> None:
    """
    Converts PyTweezer data to a LabView-compatible format.

    Args:
        pytweezers_xyz (NumPy array): bead positions loaded using 'read_pytweezers()'
        t (NumPy array): time array loaded using 'read_pytweezers()'
        path_out (str): Path to the output LabView-compatible data file.

    Returns:
        None

    This function reads PyTweezer data, reformats it to match the LabView data format,
    and writes the result to a specified output file. The output file is a tab-separated
    value (TSV) txt file (.txt) with a specific column order and data types to ensure compatibility
    with LabView software.
    """

    # obtain number of frames and number of beads tracked from the pytweezers data
    number_beads, number_frames, _ = pytweezers_xyz.shape

    # allocate an Numpy array to store the xyz positions (shape is to comply with old format). Time column will be added later
    labview_xyz = np.zeros(shape=(number_frames, number_beads * 3))

    # now reformat the data and store it into the newly allocated array
    col_nr = 0
    for bead_nr in range(number_beads):
        for axes in range(3):
            # the collumn in the new array is "the bead number, or the the bead number +1 (for y) or +2 (for z)"
            # the input data will have the x,y,z positions stored in different axes of the 3D array
            labview_xyz[:, col_nr] = pytweezers_xyz[bead_nr, :, axes]
            col_nr += 1

    # convert positions into µM, in stead of nM
    labview_xyz /= 1000.0

    # covert times into ms, in stead of seconds
    t_ms = t * 1000.0

    # convert into dataframe/ table
    column_names = [
        f"Bead_{bead_nr + 1}_{axes}"
        for bead_nr in range(number_beads)
        for axes in ["x", "y", "z"]
    ]
    labview_table = pd.DataFrame(labview_xyz, columns=column_names)

    # add time column
    labview_table["Time_ms"] = t_ms

    # add the dummy column without values. There is an additional space/tab in the original data from LabView.
    # A bit silly to add it back here, but required to make loading it back possible without having to make many exceptions. This is the most readible and clean option
    labview_table["dummy_column"] = None

    # put time column first / dummy column last
    new_order = ["Time_ms"] + column_names + ["dummy_column"]
    labview_table = labview_table[new_order]

    # write data
    # include the column with the index as this was also implied/included in original LabView output data files
    labview_table.to_csv(path_out, index=True, header=False, sep="\t")

    print(f"wrote output data into: {path_out}")
