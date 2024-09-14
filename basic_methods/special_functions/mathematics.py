'''
Commonly used functions / general mathematics 
'''
from typing import Union, List

import numpy as np 


def gaussian():
    '''
    Gaussian function 
    '''
    pass 

def exponential():
    '''
    simple exponential decay + offset 
    '''
    pass 

def line(x:Union[List[float], np.ndarray], slope:float, offset:float) -> np.ndarray:
    '''
    A line 
    '''
    a = slope 
    b = offset
    return a*x + b 



