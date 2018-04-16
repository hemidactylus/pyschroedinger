'''
    schroedinger.py :
        one-d study of integration of Schroedinger equation
        with a potential. Just to keep high-freq modes under control
'''

import matplotlib.pyplot as plt
import numpy as np
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
    integrate,
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
)

from gui import (
    doPlot,
)

def initPsi():
    return combineWFunctions(
        # 1 tunnel:
        # wGaussianPacket(0.5,0.1,-11.3095,0.5),
        # # 2 double interfering tunnel (w/ spurious)
        # wGaussianPacket(0.7,0.07,+11.3095,0.5),
        # wGaussianPacket(0.3,0.07,-11.3095,0.5),
        # 3 oscillation between two minima
        wGaussian(0.4,0.1)        
    )

def initPot():
    return combinePotentials(
        # rounded square potential (for 1, 2)
        # stepPotential(0.1,0.02,0,1000),
        # stepPotential(0.9,0.02,1000,0)
        # two-hole well (for 3)
        stepPotential(0.25,0.02,0,1000),
        stepPotential(0.75,0.02,1000,0),
        stepPotential(0.55,0.02,0,100),
        stepPotential(0.45,0.02,100,000),
    )

if __name__=='__main__':
    #
    print('Init [L=%f fm, DeltaT=%.2E fs]' % (
        toLength_fm(Lambda),
        toTime_fs(DeltaTau),
    ))
    #
    xvalues=list(range(Nx))
    psi=initPsi()
    pot=initPot()
    #
    replottable=doPlot(xvalues,psi,pot)
    #
    tau=0
    for i in itertools.count():
        for k in range(drawFreq):
            psi,normDev,tau=integrate(psi,pot,DeltaTau,tau)
        doPlot(xvalues,psi,pot,'tau=%8.4f, normdev %8.4f' % (tau,normDev), replottable)
