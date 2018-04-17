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
    miDeltaTau = complex(0,-DeltaTau)
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
    deltaPhi = [
        miDeltaTau*(d2+v*p)
        for d2,v,p in zip(secondDerivative,vPotential,Phi)
    ]
    newPhi = [
      p+dp
      for p,dp in zip(Phi,deltaPhi)
    ]
    newNorm=norm(newPhi)
    #
    return [
        p/newNorm
        for p in newPhi
    ], newNorm-1, iniTau+DeltaTau

def energy(Phi,vPotential):
    '''
        evaluates <phi|E|phi>, the adiimensional
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