'''
    tools.py : wavefunction handling tools
'''
from functools import reduce
from settings import (
    DeltaLambda,
)

def mod2(psi):
    return [
        (p.conjugate()*p).real
        for p in psi
    ]

def norm(psi):
    return (sum(mod2(psi))*DeltaLambda)**0.5

def re(psi):
    return [p.real for p in psi]

def im(psi):
    return [p.imag for p in psi]

def sumFunctions(wf1,wf2):
    return [
        p1+p2
        for p1,p2 in zip(wf1,wf2)
    ]

def combineWFunctions(*wflist,normalize=True):
    '''
        combines wave functions and optionally normalizes them
    '''
    unnormed = reduce(sumFunctions,wflist[1:],wflist[0])
    if normalize:
        psiNorm=norm(unnormed)
        return [
            p/psiNorm
            for p in unnormed
        ]
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
        return [
            v-minPot
            for v in unshifted
        ]
    else:
        return unshifted
