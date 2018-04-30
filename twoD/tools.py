'''
    tools.py : wavefunction handling tools
'''

from functools import reduce
import numpy as np

def mod2(psi):
    return (psi.conjugate()*psi).real

def norm(psi,deltaLambdaXY):
    return (sum(sum(mod2(psi)))*deltaLambdaXY)**0.5

def re(psi):
    return psi.real

def im(psi):
    return psi.imag

def sumFunctions(wf1,wf2):
    return wf1+wf2

def combineWFunctions(wflist,deltaLambdaXY,normalize=True):
    '''
        combines wave functions and optionally normalizes them
        deltaLambdaXY is the area element
    '''
    unnormed = reduce(sumFunctions,wflist[1:],wflist[0])
    if normalize:
        psiNorm=norm(unnormed,deltaLambdaXY)
        return unnormed/psiNorm
    else:
        return unnormed

def combinePotentials(potlist,shift=True):
    '''
        sums the provided potentials and optionally
        brings the minimum to zero
    '''
    unshifted = reduce(sumFunctions,potlist[1:],potlist[0])
    if shift:
        minPot=unshifted.min()
        return unshifted-minPot
    else:
        return unshifted
