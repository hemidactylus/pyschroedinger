'''
    wfunctions.py : wavefunction- and potential-
    generation tools
'''
import math
from settings import (
    Nx,
)

def wGaussianPacket(pPos,pWidth,pk,phase,weight=1):
    '''
        a Gaussian wave packet with wavenumber k
    '''
    center=pPos*Nx
    width=pWidth*Nx
    return [
        weight*complex(math.exp(-(((ni-center)/width)**2)))*complex(math.cos(phase-pk*ni/Nx),math.sin(phase-pk*ni/Nx))
        for ni in range(Nx)
    ]

def wPlaneWave(pk,phase,weight=1):
    return [
        weight*complex(math.cos(phase+pk*ni/Nx),math.sin(phase+pk*ni/Nx))
        for ni in range(Nx)
    ]

def wGaussian(pPos,pWidth,weight=1):
    '''
        a real Gaussian distribution
    '''
    return wGaussianPacket(pPos,pWidth,0.0,weight=weight)
