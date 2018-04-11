'''
    wfunctions.py : wavefunction- and potential-
    generation tools
'''
import math
from settings import (
    xSteps,
)

def wGaussianPacket(pPos,pWidth,pk,weight=1):
    '''
        a Gaussian wave packet with wavenumber k
    '''
    center=pPos*xSteps
    width=pWidth*xSteps
    return [
        weight*complex(math.exp(-(((ni-center)/width)**2)))*complex(math.cos(pk*ni/xSteps),math.sin(pk*ni/xSteps))
        for ni in range(xSteps)
    ]

def wPlaneWave(pk,phase,weight=1):
    return [
        weight*complex(math.cos(phase+pk*ni/xSteps),math.sin(phase+pk*ni/xSteps))
        for ni in range(xSteps)
    ]

def wGaussian(pPos,pWidth,weight=1):
    '''
        a real Gaussian distribution
    '''
    return wGaussianPacket(pPos,pWidth,0.0,weight=weight)
