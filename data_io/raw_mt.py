"""
Loading raw data from magnetic-tweezers

Should work both with data taken with PyTweezers and LabView (older experiments / legacy mode)

"""

import os

import numpy as np
import yaml
from labview_legacy import read_labview
from typing import IO


def read_mt_data(path: str) -> tuple[np.ndarray, np.ndarray]:
    """
    loads raw data from magnetic-tweezers (MT)

    Args:
        path (str) : absolute path to data file

    Returns:
        np.ndarray: An array with dimensions (num_beads, num_frames, 3). For every bead there is an array of (x,y,z) in the collumns and frames in the rows
        np.ndarray: The time in seconds

    Notes:
        uses file extension to check if the data has been taken using PyTweezers or LabView
    """
    # Check if pyTweezers was used to acquire the dataset
    _, extension = os.path.splitext(path)
    if extension == ".npy":
        return read_pytweezers(path)
    elif extension == ".txt":
        return read_labview(path)
    else:
        raise ValueError(
            "Not a valid file type. Pytweezers stores data as .npy and LabView as .txt"
        )


# pytweezers
def read_pytweezers(path: str) -> tuple[np.ndarray, np.ndarray]:
    """
    read raw data produced by pytweezers ('traces.npy')

    Args:
        path (str): absolute path to .npy file

    Returns:
        np.ndarray: An array with dimensions (num_beads, num_frames, 3). For every bead there is an array of (x,y,z) in the collumns and frames in the rows
        np.ndarray: The time in seconds

    Notes:
        will use the config.yaml file stored in the same folder to infer the frame rate
        pytweezer stores the data as (num_frames, num_beads, 3). For every frame you have x,y,z for every bead. Will parse it differently
    """

    # --- the following functions are taken from pytweezers.utils.data_io (and just given different names for convinience-sake) ---
    def _end_of_file(f: IO) -> bool:
        """
        check if you are at the end of the file
        """
        curpos = f.tell()
        f.seek(0, 2)
        file_size = f.tell()
        f.seek(curpos, 0)
        return curpos == file_size

    def _read_npy_in_chunks(path: str) -> np.ndarray:
        """
        load in the original data as stored by pytweezer
        """
        with open(path, "rb") as s:
            header = np.load(s, allow_pickle=True)
            if header.dtype == object:
                header = header.item()
                axis_scale = header["axisScale"]
            else:  # backwards compatibility mode
                axis_scale = header

            blocks = []
            while not _end_of_file(s):
                blk = np.load(s)
                blocks.append(blk)

        return np.concatenate(blocks) * np.array(axis_scale)[None, None]

    # --- load in the original data ----
    npy_data = _read_npy_in_chunks(path)

    # --- parse things differently ---
    num_frames = npy_data.shape[0]
    num_beads = npy_data.shape[1]
    beads_xyz = np.zeros((num_beads, num_frames, 3))
    for bead_nr in range(num_beads):
        beads_xyz[bead_nr, :, :] = npy_data[:, bead_nr, :]

    # -- time in seconds ---
    # get frame rate from config file
    dirname = os.path.dirname(path)
    fn_config = os.path.join(dirname, "config.yaml")
    with open(fn_config, "r") as f:
        pytw_config = yaml.safe_load(f)
    frame_rate = pytw_config["framerate"]

    # determine time
    t = (1.0 / frame_rate) * np.arange(num_frames)
    return beads_xyz, t
