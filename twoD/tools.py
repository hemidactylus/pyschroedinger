'''
    tools.py : wavefunction handling tools
'''

from functools import reduce
import numpy as np

def mod2(psi):
    return (psi.conjugate()*psi).real

def norm(psi,deltaLambdaXY,slices=None):
    '''
        if slices are requested, those are
        integer indices for the one-dimensional Nx*Ny full psi
        and the second argument is a map of partial norms
        each pertaining to a slice.
        It is responsibility of the caller to ensure the slices
        are a proper partition. The slices are a list such as:
            [0, i1, i2 ... in] where in < total_size
    '''
    if slices is None:
        return (sum(mod2(psi))*deltaLambdaXY)**0.5,None
    else:
        _mod2=mod2(psi)
        normMap={
            slIndex: sum(_mod2[slStart:slEnd])
            for slIndex,(slStart,slEnd) in enumerate(zip(slices,slices[1:]+[None]))
        }
        fullNorm=sum(normMap.values())
        return (fullNorm*deltaLambdaXY)**0.5,{k: v/fullNorm for k,v in normMap.items()}

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
        psiNorm,_=norm(unnormed,deltaLambdaXY,slices=None)
        return unnormed/psiNorm
    else:
        return unnormed

def combinePotentials(potlist,shift=True,matrixRepo=None):
    '''
        sums the provided potentials and optionally
        brings the minimum to zero
    '''
    if matrixRepo is None:
        unshifted = reduce(sumFunctions,potlist[1:],potlist[0])
        if shift:
            minPot=unshifted.min()
            return unshifted-minPot
        else:
            return unshifted
    else:
        np.copyto(matrixRepo['fullPotential'],potlist[0])
        for pot in potlist[1:]:
            matrixRepo['fullPotential']+=pot
        if shift:
            minPot=matrixRepo['fullPotential'].min()
            return matrixRepo['fullPotential']-minPot
        else:
            return matrixRepo['fullPotential']
