'''
    dynamics.py : integration of the Schroedinger equation
'''

from settings import (
    xSize,
    xSteps,
    deltaT,
    hbar,
    m,
    periodicBC,
)

from tools import (
  mod2,
  norm,
  re,
  im,
)

def integrate(psi,pot,deltaT):
    '''
        returns the new psi
    '''
    deltaX2=(xSize/xSteps)**2
    kinFactor=-(hbar**2)*(2*m)
    if periodicBC:
        diff2 = [
            kinFactor*(2*p-pl-pr)/deltaX2
            for pl,p,pr in zip(
                psi[1:]+[psi[0]],
                psi,
                [psi[-1]]+psi[:-1],
            )
        ]
    else:
        diff2 = [complex(0)] + [
            kinFactor*(2*p-pl-pr)/deltaX2
            for pl,p,pr in zip(psi[:-2],psi[1:-1],psi[2:])
        ] + [complex(0)]

    invIHT = deltaT/(complex(0,hbar))
    deltaPsi = [
        invIHT*(d2+v*p)
        for d2,v,p in zip(diff2,pot,psi)
    ]
    newPsi = [
      p+dp
      for p,dp in zip(psi,deltaPsi)
    ]
    newNorm=norm(newPsi)
    #
    return [
        p/newNorm
        for p in newPsi
    ], newNorm-1
