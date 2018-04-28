'''
    tools.py : wavefunction handling tools
'''

import numpy as np

def mod2(psi):
    return (psi.conjugate()*psi).real

# def norm(psi,deltaLambda):
#     return (sum(mod2(psi))*deltaLambda)**0.5

def re(psi):
    return psi.real

def im(psi):
    return psi.imag
