'''
    dynamics.py : integration of the Schroedinger equation
'''

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
        returns the new Phi
    '''

    newPhi = [
      p+DeltaTau*dp
      for p,dp in zip(Phi,evolutionOperator(Phi,vPotential))
    ]
    newNorm=norm(newPhi)
    #
    return [
        p/newNorm
        for p in newPhi
    ], newNorm-1, iniTau+DeltaTau

def integrateK4(Phi,vPotential,DeltaTau,iniTau):
    '''
        Attempt at Runge-Kutta of fourth order
    '''
    halfDT=DeltaTau*0.5
    k1 = evolutionOperator(Phi,vPotential)
    k2 = evolutionOperator(
        [
            p+p1*halfDT
            for p,p1 in zip(Phi,k1)
        ],
        vPotential
    )
    k3=evolutionOperator(
        [
            p+p2*halfDT
            for p,p2 in zip(Phi,k2)
        ],
        vPotential
    )
    k4=evolutionOperator(
        [
            p+p3*DeltaTau
            for p,p3 in zip(Phi,k3)
        ],
        vPotential
    )
    npFactor=DeltaTau/6.0
    newPhi=[
        p+npFactor*(p1+2*p2+2*p3+p4)
        for p,p1,p2,p3,p4 in zip (
            Phi,
            k1,
            k2,
            k3,
            k4,
        )
    ]
    #
    newNorm=norm(newPhi)
    #
    return [
        p/newNorm
        for p in newPhi
    ], newNorm-1, iniTau+DeltaTau

def evolutionOperator(Phi,vPotential):
    '''
        given wf and potential, (and using mu and lambda),
        evaluates F in
            delta Phi/delta tau = F(lambda,phi)
        i.e.
            F = -i ( (/1(2mu)) delta2phi/deltalambda2 + v*phi )
    '''
    if periodicBC:
        secondDerivative = [
            KineticFactor*(2*p-pl-pr)/DeltaLambda2
            for pl,p,pr in zip(
                Phi[1:]+[Phi[0]],
                Phi,
                [Phi[-1]]+Phi[:-1],
            )
        ]
    else:
        # here the boundary cases are dangerous for exploding solutions
        secondDerivative = [complex(0)] + [
            KineticFactor*(2*p-pl-pr)/DeltaLambda2
            for pl,p,pr in zip(Phi[:-2],Phi[1:-1],Phi[2:])
        ] + [complex(0)]
    #
    minusI = complex(0,-1)
    F = [
        minusI*(d2+v*p)
        for d2,v,p in zip(secondDerivative,vPotential,Phi)
    ]
    return F

def energy(Phi,vPotential):
    '''
        evaluates <phi|E|phi>, the adimensional
        version of <psi|E|psi>
    '''
    if periodicBC:
        secondDerivative = [
            KineticFactor*(2*p-pl-pr)/DeltaLambda2
            for pl,p,pr in zip(
                Phi[1:]+[Phi[0]],
                Phi,
                [Phi[-1]]+Phi[:-1],
            )
        ]
    else:
        # here the boundary cases are dangerous for exploding solutions
        secondDerivative = [complex(0)] + [
            KineticFactor*(2*p-pl-pr)/DeltaLambda2
            for pl,p,pr in zip(Phi[:-2],Phi[1:-1],Phi[2:])
        ] + [complex(0)]
    #
    complexEn = sum(
        p.conjugate()*(d2+v*p)
        for d2,v,p in zip (secondDerivative,vPotential,Phi)
    )
    if abs(complexEn.imag) > 0.001*abs(complexEn.real):
        raise ValueError('Energy substantially complex: %f | %f' % (complexEn.real,complexEn.imag))
    return complexEn.real