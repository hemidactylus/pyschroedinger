'''
    dynamics.py
'''

import numpy as np
import time

def evolve(phi):
    '''
        fake for now
    '''
    time.sleep(0.01)
    return np.vstack([phi[1:],[phi[0]]])