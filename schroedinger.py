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
        # wGaussian(0.5,0.04,1.0),
        wGaussianPacket(0.5,0.1,-20*math.pi,0.5),
        # wPlaneWave(10*math.pi,0.2,weight=0.2),
        # wPlaneWave(-4*math.pi,0.5,weight=1.0),
    )

def initPot():
    return combinePotentials(
        #freeParticle(),
        #harmonicPotential(0.5,PotV),
        stepPotential(0.1,0.02,0,1000),
        stepPotential(0.9,0.02,1000,0)
    )

if __name__=='__main__':
    #
    print('Init [L=%f fm, DeltaT=%f fs]' % (
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
