#!/usr/bin/env python

'''
    schroedinger.py :
      two-dimensional study of integration of the
      Schroedinger equation
'''
from itertools import count
import time
import sys

from twoD.settings import (
    Nx,
    Ny,
)

from twoD.gui import (
    doPlot,
)

import numpy as np

def initPhi(sigma2=0.2):
    # very fake for now
    # (Phi is the *complex* quantity)
    phi=np.zeros((Nx,Ny),dtype=complex)
    for x in range(Nx):
        for y in range(Ny):
            _x=(x/Nx)-0.5
            _y=(y/Ny)-0.5
            amp=np.exp(-(_x**2+_y**2)/sigma2)
            pha=np.pi*_x
            phi[x][y]=complex(amp*np.cos(pha),amp*np.sin(pha))
    return phi

if __name__=='__main__':

    phi=initPhi()
    replotting=doPlot(phi)

    for i in count():
        #
        print('Round %i ... ' % i, end='')
        sys.stdout.flush()
        #
        phi=initPhi(sigma2=0.04+0.3*(np.cos(i/5)**2))
        doPlot(phi,replotting)
        #
        print('done.')
        sys.stdout.flush()
