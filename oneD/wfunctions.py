'''
    wfunctions.py : wavefunction- and potential-
    generation tools
'''
import math
import numpy as np

from oneD.settings import (
    Nx,
    waveNumber0,
    deltaLambda,
)

def wGaussianPacket(pPos,pWidth,ph0,phase=0.0,weight=1):
    '''
        a Gaussian wave packet with (dimensionless) wavenumber ph
        NOTE:   wave is exp(i*h*lambda) = exp(i*k*x),
                then h = k / (m_e * c / hbar )
                Wave numbers are automatically rounded for continuity
    '''
    ph=roundWaveNumber(ph0)
    center=pPos*Nx
    width=pWidth*Nx
    return np.array([
        weight*complex(math.exp(-(((ni-center)/width)**2)))*complex(
            math.cos(phase-ph*ni*deltaLambda),
            math.sin(phase-ph*ni*deltaLambda),
        )
        for ni in range(Nx)
    ])

def wPlaneWave(ph0,phase=0.0,weight=1):
    ph=roundWaveNumber(ph0)
    return np.array([
        weight*complex(
            math.cos(phase+ph*ni*DeltaLambda),
            math.sin(phase+ph*ni*DeltaLambda),
        )
        for ni in range(Nx)
    ])

def wGaussian(pPos,pWidth,weight=1):
    '''
        a real Gaussian distribution
    '''
    return wGaussianPacket(pPos,pWidth,0.0,weight=weight)

def roundWaveNumber(ph):
    '''
        given a wave number ph, rounds it to the
        nearest even multiple of h0
    '''
    if ph==0:
        return ph
    else:
        sign=+1 if ph>0 else -1
        #
        roundedM = sign*int(0.5+abs(ph/waveNumber0))
        print('Rounding %f => %i times h0' % (ph/waveNumber0,roundedM))
        return roundedM * waveNumber0
