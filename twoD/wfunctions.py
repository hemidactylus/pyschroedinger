'''
    wfunctions.py
'''

import numpy as np

def wavePacket(Nx,Ny,c,ph0,sigma2,
    waveNumber0,deltaLambdaX,deltaLambdaY,
    phase=0.0,weight=1):
    ph=(
        roundWaveNumber(ph0[0],waveNumber0,0),
        roundWaveNumber(ph0[1],waveNumber0,1),
    )
    # (Phi is the *complex* quantity)
    phi=np.zeros((Nx,Ny),dtype=complex)
    for x in range(Nx):
        for y in range(Ny):
            _x=(x/(Nx-1))
            _y=(y/(Ny-1))
            amp=weight*np.exp(-((_x-c[0])**2/sigma2[0]+(_y-c[1])**2/sigma2[1]))
            pha=phase+(x*deltaLambdaX*ph[0])+(y*deltaLambdaY*ph[1])
            phi[x][y]=complex(amp*np.cos(pha),amp*np.sin(pha))
    return phi.reshape((Nx*Ny))

def roundWaveNumber(ph,waveNumber0,axis):
    '''
        axis=0 for x, 1 for y
    '''
    if ph==0:
        return ph
    else:
        sign=+1 if ph>0 else -1
        #
        roundedM = sign*int(0.5+abs(ph/waveNumber0[axis]))
        return roundedM * waveNumber0[axis]
