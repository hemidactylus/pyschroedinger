'''
    potentials.py : generation of potentials
'''

from settings import (
    xSteps,
)

def freeParticle():
    '''
        generates a potential for 'freeParticle'
    '''
    return [0]*xSteps

def harmonic(pPos,weight):
    '''
        generates a potential for 'harmonic'
    '''
    center=pPos*n
    return [
        weight*(ni-center)**2
        for ni in range(xSteps)
    ]

    '''
#
potCenter=0.7
potAmplitude=0#0.1
potWidth=0.001
#
potStep=0.3
potHeight=0.05
potStepThickness=0.03
    '''

def stepPotential():
    '''
        generates a potential for 'stepPotential'
    '''
    pass
    # a step on the left
    # potStepLocation=potStep*n
    # potStepWidth=potStepThickness*n
    # unsubPot = [
    #     potHeight*((1+math.tanh((potStepLocation-ni)/potStepWidth))/2)
    #     for ni in range(n)
    # ]

def exponentialWall():
    '''
        generates a potential for 'exponentialWall'
    '''
    pass
    # # exp borders
    # potThickness=potWidth*n
    # unsubPot = [
    #     pAmplitude*((math.exp((potThickness/(n-ni))+(potThickness/(ni+1)))))
    #     for ni in range(n)
    # ]
