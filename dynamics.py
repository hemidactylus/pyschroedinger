'''
    dynamics.py : integration of the Schroedinger equation
'''

import numpy as np

from settings import (
    DeltaLambda2,
    KineticFactor,
    periodicBC,
)

from tools import (
  mod2,
  norm,
  re,
  im,
)

def integrate(Phi,vPotential,DeltaTau, iniTau):
    '''
        returns the new Phi after DeltaTau (and other things)
    '''

    newPhi = Phi+DeltaTau*evolutionOperator(Phi,vPotential)
    newNorm=norm(newPhi)
    #
    return newPhi/newNorm, newNorm-1, iniTau+DeltaTau

def integrateK4(Phi,vPotential,DeltaTau,iniTau):
    '''
        Runge-Kutta of fourth order
    '''
    halfDT=DeltaTau*0.5
    k1 = evolutionOperator(Phi,vPotential)
    k2 = evolutionOperator(
        Phi+k1*halfDT,
        vPotential
    )
    k3=evolutionOperator(
        Phi+k2*halfDT,
        vPotential
    )
    k4=evolutionOperator(
        Phi+DeltaTau*k3,
        vPotential
    )
    npFactor=DeltaTau/6.0
    newPhi=Phi+npFactor*(k1+2*k2+2*k3+k4)
    #
    newNorm=norm(newPhi)
    #
    return newPhi/newNorm, newNorm-1, iniTau+DeltaTau

def evolutionOperator(Phi,vPotential):
    '''
        given wf and potential, (and using mu and lambda),
        evaluates F in
            delta Phi/delta tau = F(lambda,phi)
        i.e.
            F = -i ( (/1(2mu)) delta2phi/deltalambda2 + v*phi )
    '''
    if periodicBC:
        enlargedPhi=np.hstack([Phi[-1:],Phi,Phi[:1]])
        secondDerivative=KineticFactor*(2*Phi-enlargedPhi[:-2]-enlargedPhi[2:])/DeltaLambda2
    else:
        secondDerivative=np.hstack([
            complex(0),
            KineticFactor*(2*Phi[1:-1]-Phi[:-2]-Phi[2:])/DeltaLambda2,
            complex(0),
        ])
    #
    minusI = complex(0,-1)
    F = minusI*(secondDerivative+vPotential*Phi)
    return F

def energy(Phi,vPotential):
    '''
        evaluates <phi|E|phi>, the adimensional
        version of <psi|E|psi>
    '''
    if periodicBC:
        enlargedPhi=np.hstack([Phi[-1:],Phi,Phi[:1]])
        secondDerivative=KineticFactor*(2*Phi-enlargedPhi[:-2]-enlargedPhi[2:])/DeltaLambda2
    else:
        secondDerivative=np.hstack([
            complex(0),
            KineticFactor*(2*Phi[1:-1]-Phi[:-2]-Phi[2:])/DeltaLambda2,
            complex(0),
        ])
    #
    complexEn = sum(
        p.conjugate()*(d2+v*p)
        for d2,v,p in zip (secondDerivative,vPotential,Phi)
    )
    if abs(complexEn.imag) > 0.001*abs(complexEn.real):
        raise ValueError('Energy substantially complex: %f | %f' % (complexEn.real,complexEn.imag))
    return complexEn.real