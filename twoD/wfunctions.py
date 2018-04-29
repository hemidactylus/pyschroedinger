'''
    wfunctions.py
'''

import numpy as np

def makeFakePhi(Nx,Ny,cx,cy,sigma2,amplitude):
    # (Phi is the *complex* quantity)
    phi=np.zeros((Nx,Ny),dtype=complex)
    for x in range(Nx):
        for y in range(Ny):
            _x=(x/Nx)
            _y=(y/Ny)
            amp=amplitude*np.exp(-((_x-cx)**2+(_y-cy)**2)/sigma2)
            pha=np.pi*_x
            phi[x][y]=complex(amp*np.cos(pha),amp*np.sin(pha))
    return phi
