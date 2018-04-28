'''
    potentials.py : generation of potentials
'''

import math
import numpy as np

from oneD.settings import (
    Nx,
)

def freeParticle():
    '''
        generates a potential for 'freeParticle'
    '''
    return np.array([0]*Nx)

def harmonicPotential(pPos,weight):
    '''
        generates a potential for 'harmonic'
    '''
    center=pPos*Nx
    return np.array([
        weight*(ni-center)**2
        for ni in range(Nx)
    ])

def stepPotential(pPos,pThickness,vLeft,vRight):
    '''
        A step with finite thickness
    '''
    center=pPos*Nx
    thickness=pThickness*Nx
    unsubPot = np.array([
        vLeft+(vRight-vLeft)*((1+math.tanh((center-ni)/thickness))/2)
        for ni in range(Nx)
    ])
    return unsubPot

def exponentialWall(pPos,rate,amplitude):
    '''
        exponentialWall potential: pPos must sensibly be > 1 or < 0,
        then:
            pot(x) = amplitude*exp(rate/(abs(pPos-x)))
    '''
    center=pPos*Nx-0.5
    unsubPot = np.array([
        amplitude*((math.exp(rate/(abs(center-ni)))))
        for ni in range(Nx)
    ])
    return unsubPot
