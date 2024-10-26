'''
Convert raw data from PyTweezer to LabView's format to use older GUIs 

-- Misha, October 2024 
'''
from .raw_mt import read_mt_data
import pandas as pd 
import numpy as np 
import sys 
import os 


def pytweezer_to_labview(path_in:str, path_out: str) -> None:
    """
    Converts PyTweezer data to a LabView-compatible format.

    Args:
        path_in (str): Path to the input PyTweezer data file.
        path_out (str): Path to the output LabView-compatible data file.

    Returns:
        None

    This function reads PyTweezer data, reformats it to match the LabView data format,
    and writes the result to a specified output file. The output file is a tab-separated
    value (TSV) txt file (.txt) with a specific column order and data types to ensure compatibility
    with LabView software.
    """

    # read the pytweezer data 
    pytweezer_xyz, t = read_mt_data(path_in)

    # obtain numnber of frames and number of beads tracked from the pytweezer data 
    nmbr_beads, nmbr_frames, _ = pytweezer_xyz.shape 

    # allocate an Numpy array to store the xyz positions (shape is to comply with old format). Time collumn will be added later
    labview_xyz = np.zeros( shape = (nmbr_frames, nmbr_beads*3))


    # now reformat the data and store it into the newly alllocated array
    col_nr = 0 
    for bead_nr in range(nmbr_beads):
        for axes in range(3):
            # the collumn in the new array is "the bead number, or the the bead number +1 (for y) or +2 (for z)"
            # the input data will have the x,y,z positions stored in different axes of the 3D array 
            labview_xyz[:, col_nr] = pytweezer_xyz[bead_nr, :, axes]
            col_nr += 1 
        
    # convert positions into µM, in stead of nM 
    labview_xyz /= 1000. 

    # covert times into ms, in stead of seconds 
    t_ms = t * 1000. 

    # convert into dataframe/ table 
    column_names = [f"Bead_{bead_nr+1}_{axes}" for bead_nr in range(nmbr_beads) for axes in ["x","y","z"]]
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
    labview_table.to_csv(path_out, index=True, header=False, sep='\t')

    print(f"wrote output data into: {path_out}")




