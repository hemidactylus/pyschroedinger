#!/usr/bin/env python

'''
    schroedinger.py :
        one-d study of integration of Schroedinger equation
        with a potential. Just to keep high-freq modes under control
'''

import matplotlib.pyplot as plt
import math
import itertools

from oneD.settings import (
    Lambda,
    Nx,
    deltaTau,
    deltaLambda,
    drawFreq,
    framesToDraw,
    periodicBC,
    Mu,
    integratorMap,
)

from oneD.dynamics import (
    energy,
)

from oneD.tools import (
    mod2,
    norm,
    re,
    im,
    combineWFunctions,
    combinePotentials,
)

from oneD.wfunctions import (
    wGaussianPacket,
    wGaussian,
    wPlaneWave,
    roundWaveNumber,
)

from oneD.potentials import (
    freeParticle,
    harmonicPotential,
    stepPotential,
    exponentialWall,
)

from utils.units import (
    toLength_fm,
    toTime_fs,
    toEnergy_MeV,
)

from oneD.gui import (
    doPlot,
)

def initPhi():
    return combineWFunctions(
        [
            # 1 tunnel (with periodic BC):
            wGaussianPacket(0.2,0.1,5.65,0.5),
            # wGaussianPacket(0.9,0.05,-5.65,0.1),
            # # 2 double interfering tunnel (w/ spurious)
            # wGaussianPacket(0.7,0.07,+11.3095,0.5),
            # wGaussianPacket(0.3,0.07,-11.3095,0.5),
            # 3 oscillation between two minima
            # wGaussian(0.36,0.07),
            # 4. test centered gaussians
            # wGaussian(0.35,0.1,weight=0.3),
            # wGaussian(0.65,0.1,weight=0.7),
            # 5. two symmetrical gaussians
            # wGaussian(0.35,0.07),
            # wGaussian(0.65,0.07),
            # 6. a small packet
            # wGaussianPacket(0.5,0.05,8,0.5),
        ],
        deltaLambda=deltaLambda,
    )

def initPot():
    return combinePotentials(
        [
            # free particle
            stepPotential(0.5,0.1,0,0),
            # rounded square potential (for 1, 2)
            stepPotential(0.4,0.02,280,0),
            stepPotential(0.6,0.02,0,280),
            # two-hole well (for 3)
            # stepPotential(0.25,0.01,0,1000),
            # stepPotential(0.75,0.01,1000,0),
            # stepPotential(0.55,0.01,0,80),
            # stepPotential(0.45,0.01,80,000),
            # 5: lower-barrier rounded square box
            # stepPotential(0.1,0.02,0,100),
            # stepPotential(0.9,0.02,100,0)
            # 6. thick high walls to check for open BC
            # stepPotential(0.35,0.015,0,8000),
            # stepPotential(0.65,0.015,8000,0)
            
            # exponentialWall(1.01,0.95,1000),
            # exponentialWall(-0.01,0.95,1000)
        ],
    )

if __name__=='__main__':
    #
    print('Init [L=%f fm, DeltaT=%.2E fs]' % (
        toLength_fm(Lambda),
        toTime_fs(deltaTau),
    ))
    #
    xvalues=list(range(Nx))
    phi=initPhi()
    pot=initPot()
    # now the map of evolutions
    phiMap={
        k: phi
        for k in integratorMap.keys()
    }
    normDevMap={k: None for k in integratorMap.keys()}
    tauIncrMap={k: None for k in integratorMap.keys()}
    energyMap={k: None for k in integratorMap.keys()}
    replottable=doPlot(xvalues,phiMap,pot)
    #
    tau=0

    integrators={
        k: v(
            wfSize=Nx,
            deltaTau=deltaTau,
            deltaLambda=deltaLambda,
            nIntegrationSteps=drawFreq,
            vPotential=pot,
            periodicBC=periodicBC,
            mu=Mu,
        )
        for k,v in integratorMap.items()
    }

    import time
    ini=time.time()
    for i in range(framesToDraw) if framesToDraw is not None else itertools.count():
        for k,v in integrators.items():
            phiMap[k],normDevMap[k],tauIncrMap[k]=v.integrate(phiMap[k],drawFreq)
            energyMap[k]=energy(phiMap[k],pot,periodicBC,deltaLambda,Mu)
        assert(len(set(tauIncrMap.values()))==1)
        tau+=list(tauIncrMap.values())[0]

        descText='[f=%6i, stp=%6i] t=%.3E fs\n%s' % (
            i,
            i*drawFreq,
            toTime_fs(tau),
            '\n'.join(
                '%s: E=%+.3E MeV (nd=%+.3E)' % (
                    k,
                    toEnergy_MeV(energyMap[k]),
                    normDevMap[k],
                )
                for k in sorted(integrators.keys())
            )
        )

        doPlot(
            xvalues,
            phiMap,
            pot,
            descText,
            replottable,
            # photoIndex=i,
        )
    print('done in %f seconds' % (time.time()-ini))
