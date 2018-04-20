'''
    schroedinger.py :
        one-d study of integration of Schroedinger equation
        with a potential. Just to keep high-freq modes under control
'''

import matplotlib.pyplot as plt
import math
import itertools

from settings import (
    Lambda,
    Nx,
    DeltaTau,
    drawFreq,
    PotV,
)

from dynamics import (
    #integrate as integrate,
    integrateK4 as integrate,
    energy,
)

from tools import (
    mod2,
    norm,
    re,
    im,
    combineWFunctions,
    combinePotentials,
)

from wfunctions import (
    wGaussianPacket,
    wGaussian,
    wPlaneWave,
    roundWaveNumber,
)

from potentials import (
    freeParticle,
    harmonicPotential,
    stepPotential,
    exponentialWall,
)

from units import (
    toLength_fm,
    toTime_fs,
    toEnergy_Mev,
)

from gui import (
    doPlot,
)

def initPhi():
    return combineWFunctions(
        # 1 tunnel:
        wGaussianPacket(0.5,0.1,5.65,0.5),
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
    )

def initPot():
    return combinePotentials(
        # rounded square potential (for 1, 2)
        stepPotential(0.1,0.02,0,400),
        stepPotential(0.9,0.02,400,0)
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
    )

if __name__=='__main__':
    #
    print('Init [L=%f fm, DeltaT=%.2E fs]' % (
        toLength_fm(Lambda),
        toTime_fs(DeltaTau),
    ))
    #
    xvalues=list(range(Nx))
    phi=initPhi()
    pot=initPot()
    #
    replottable=doPlot(xvalues,phi,pot)
    #
    tau=0
    for i in itertools.count():
        for k in range(drawFreq):
            phi,normDev,tau=integrate(phi,pot,DeltaTau,tau)
        phiEnergy=energy(phi,pot)
        doPlot(
            xvalues,
            phi,
            pot,
            't=%.4E fs, normdev %.4E, E=%.4E MeV' % (
                toTime_fs(tau),
                normDev,
                toEnergy_Mev(phiEnergy.real),
            ),
            replottable,
        )
