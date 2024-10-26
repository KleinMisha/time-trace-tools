'''
Loading raw data from magnetic-tweezers

Should work both with data taken with PyTweezers and LabView (older experiments / legacy mode)

'''
import os 
import sys
import yaml 
from typing import Union, Tuple, Dict, List, Any, Callable 

import numpy as np
import pandas as pd  

def read_mt_data(path: str) -> Tuple[np.ndarray, np.ndarray]:
    '''
    loads raw data from magnetic-tweezers (MT)

    Args:
        path (str) : absolute path to data file 
    
    Returns: 
        np.ndarray: An array with dimensions (num_beads, num_frames, 3). For every bead there is an array of (x,y,z) in the collumns and frames in the rows
        np.ndarray: The time in seconds 

    Notes:
        uses file extension to check if the data has been taken using PyTweezers or LabView
    '''
    # Check if pyTweezers was used to acquire the dataset 
    _, extension = os.path.splitext(path)
    if extension == '.npy':
        return read_pytweezers(path)
    elif extension == '.txt': 
        return read_labview(path)
    else:
        raise ValueError("Not a vallid file type. Pytweezers stores data as .npy and LabView as .txt") 

# pytweezers 
def read_pytweezers(path: str) -> Tuple[np.ndarray, np.ndarray]:
    '''
    read raw data produced by pytweezers ('traces.npy')

    Args:
        path (str): absolute path to .npy file 

    Returns:
        np.ndarray: An array with dimensions (num_beads, num_frames, 3). For every bead there is an array of (x,y,z) in the collumns and frames in the rows
        np.ndarray: The time in seconds 
 
    Notes:
        will use the config.yaml file stored in the same folder to infer the frame rate 
        pytweezer stores the data as (num_frames, num_beads, 3). For every frame you have x,y,z for every bead. Will parse it differently
    '''
    # --- the following functions are taken from pytweezer.utils.data_io (and just given different names for convinience-sake) --- 
    def _end_of_file(f: object) -> bool:
        '''
        check if you are at the end of the file
        '''
        curpos = f.tell()
        f.seek(0,2)
        file_size = f.tell()
        f.seek(curpos,0)
        return curpos == file_size 

    def _read_npy_in_chunks(path: str) -> np.ndarray:
        '''
        load in the original data as stored by pytweezer
        '''
        with open(path, 'rb') as s:
            header = np.load(s, allow_pickle=True)
            if header.dtype == object:
                header = header.item()
                axis_scale = header['axisScale']
            else: # backwards compatibility mode
                axis_scale = header

            blocks = []
            while not _end_of_file(s):
                blk = np.load(s)
                blocks.append(blk)

        return np.concatenate(blocks) * np.array(axis_scale)[None,None]

    # --- load in the original data ---- 
    npy_data = _read_npy_in_chunks(path)

    # --- parse things differently --- 
    num_frames = npy_data.shape[0]
    num_beads  = npy_data.shape[1]
    beads_xyz = np.zeros((num_beads, num_frames, 3))
    for bead_nr in range(num_beads):
        beads_xyz[bead_nr,:,:] = npy_data[:,bead_nr,:]
    
    # -- time in seconds --- 
    # get frame rate from config file 
    dirname = os.path.dirname(path)
    fn_config = os.path.join(dirname, "config.yaml")
    with open(fn_config, 'r') as f:
        pytw_config = yaml.safe_load(f)
    frame_rate = pytw_config['framerate']

    # determine time 
    t = (1./frame_rate) * np.arange(num_frames)
    return beads_xyz, t 


# LabView :: Older data is taken before we had pytweezers, but we still want to inspect things the same way 
def read_labview(path: str) -> Tuple[np.ndarray, np.ndarray]:
    '''
    read raw data produced by LabView ('.txt')

    Args:
        path (str): absolute path to .txt file 

    Returns:
        np.ndarray: An array with dimensions (num_beads, num_frames, 3). For every bead there is an array of (x,y,z) in the collumns and frames in the rows
        np.ndarray: The time in seconds 

    Notes: 
        reads the original .txt as a table, renames the collumns to more easily group together (x,y,z) of the same column
        NOTE: possibly could be done more efficient, but this is sufficient for now 
    '''

    # ---- load file ----
    try:
        data = pd.read_table(path, header=None, dtype='float32')
    except:
        data = pd.read_table(path, header=None)



    # - every bead has three columns: x,y,z. First column is time in milliseconds.
    num_columns = len(data.columns)
    num_beads = (num_columns - 1) // 3
    num_frames = len(data)


    # --- drop the final column with NaNs and the first collumn with just the index ---
    data.drop(columns=data.columns[[0, -1]], inplace=True)
    
    # rename the columns in the data 
    column_names = ["Time_ms"]
    for bead_nr in range(num_beads):
        for suffix in ["_x", "_y", "_z"]:
            column_names.append(f"Bead_{bead_nr + 1}" + suffix)
    rename_dict = {data.columns[i]: column_names[i] for i in range(len(column_names))}
    data.rename(mapper=rename_dict, axis='columns', inplace=True) 


    # --- Build the output array:  allocate X,Y,Z data as 3D np.array --- 
    beads_xyz = np.zeros((num_beads, num_frames, 3))
    for bead_nr in range(num_beads):
        cols = [f"Bead_{bead_nr+1}_{ax}" for ax in ['x','y','z']]
        one_bead = data[cols].values
        beads_xyz[bead_nr, :,:] = one_bead
    
    # -- time array ---- 
    t = data['Time_ms'].values / 1000.
    return beads_xyz, t 


    

