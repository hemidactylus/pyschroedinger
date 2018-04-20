'''
    potentials.py : generation of potentials
'''

import math

from settings import (
    Nx,
)

def freeParticle():
    '''
        generates a potential for 'freeParticle'
    '''
    return [0]*Nx

def harmonicPotential(pPos,weight):
    '''
        generates a potential for 'harmonic'
    '''
    center=pPos*Nx
    return [
        weight*(ni-center)**2
        for ni in range(Nx)
    ]

def stepPotential(pPos,pThickness,vLeft,vRight):
    '''
        A step with finite thickness
    '''
    center=pPos*Nx
    thickness=pThickness*Nx
    unsubPot = [
        vLeft+(vRight-vLeft)*((1+math.tanh((center-ni)/thickness))/2)
        for ni in range(Nx)
    ]
    return unsubPot

def exponentialWall(pPos,rate,amplitude):
    '''
        exponentialWall potential: pPos must sensibly be > 1 or < 0,
        then:
            pot(x) = amplitude*exp(rate/(abs(pPos-x)))
    '''
    center=pPos*Nx-0.5
    unsubPot = [
        amplitude*((math.exp(rate/(abs(center-ni)))))
        for ni in range(Nx)
    ]
    return unsubPot