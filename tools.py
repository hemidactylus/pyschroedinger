'''
    tools.py : wavefunction handling tools
'''

from functools import reduce
import numpy as np

from settings import (
    deltaLambda,
)

def mod2(psi):
    return (psi.conjugate()*psi).real

def norm(psi):
    return (sum(mod2(psi))*deltaLambda)**0.5

def re(psi):
    return psi.real

def im(psi):
    return psi.imag

def sumFunctions(wf1,wf2):
    return wf1+wf2

def combineWFunctions(*wflist,normalize=True):
    '''
        combines wave functions and optionally normalizes them
    '''
    unnormed = reduce(sumFunctions,wflist[1:],wflist[0])
    if normalize:
        psiNorm=norm(unnormed)
        return unnormed/psiNorm
    else:
        return unnormed

def combinePotentials(*potlist,shift=True):
    '''
        sums the provided potentials and optionally
        brings the minimum to zero
    '''
    unshifted = reduce(sumFunctions,potlist[1:],potlist[0])
    if shift:
        minPot=min(unshifted)
        return unshifted-minPot
    else:
        return unshifted
