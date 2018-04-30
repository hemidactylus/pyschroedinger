'''
    wfunctions.py
'''

import numpy as np

def makeFakePhi(Nx,Ny,cx,cy,sigma2,amplitude):
    # (Phi is the *complex* quantity)
    phi=np.zeros((Nx,Ny),dtype=complex)
    for x in range(Nx):
        for y in range(Ny):
            _x=(x/(Nx-1))
            _y=(y/(Ny-1))
            amp=amplitude*np.exp(-((_x-cx)**2+(_y-cy)**2)/sigma2)
            pha=np.pi*_x*10+np.pi*_y*5
            phi[x][y]=complex(amp*np.cos(pha),amp*np.sin(pha))
    return phi
