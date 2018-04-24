'''
    dynamics.py : integration of the Schroedinger equation
'''

import numpy as np

from settings import (
    DeltaLambda2,
    KineticFactor,
    periodicBC,
    Nx,
    Mu,
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

####

def MK4EvolutionMatrixH(vPotential,DeltaTau):
    sF=DeltaTau*evolutionMatrixF(vPotential)
    H=(sF+sF.dot(sF)/2.+sF.dot(sF).dot(sF)/6.+sF.dot(sF).dot(sF).dot(sF)/24.)
    return H

def evolutionMatrixF(vPotential):
    '''
        returns a Nx*Nx matrix with (i/2mu)(kinetic)-i(v)
    '''
    # the kinetic part
    kinPart=np.diag(2*np.ones(Nx))
    for i in range(Nx):
        kinPart[i,(i+1)%Nx]=-1
        kinPart[(i+1)%Nx,i]=-1
    if not periodicBC:
        kinPart[Nx-1,0]=0
        kinPart[0,Nx-1]=0
    # together with the potential is the final result
    mKinFactor=complex(0,1.0/(2.0*float(Mu)))
    return mKinFactor*kinPart+complex(0,-1)*np.diag(vPotential)

def integrateMK4(Phi,evoH,_ignored_dt,iniTau):
    '''
        a matrix approach to RK4.
        DeltaTau is IGNORED
    '''
    newPhi = evoH.dot(Phi)
    # newPhi = Phi+evoH.dot(Phi)

    newNorm=norm(newPhi)
    #
    return newPhi/newNorm, newNorm-1, iniTau+_ignored_dt

####

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