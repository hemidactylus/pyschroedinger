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
    Nx,
    DeltaTau,
    drawFreq,
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

from gui import (
    doPlot,
)

def initPsi():
    return combineWFunctions(
        wGaussian(0.5,0.04,1.0),
        # wGaussianPacket(0.45,0.02,20*math.pi,0.5),
        # wPlaneWave(10*math.pi,0.2,weight=0.2),
        # wPlaneWave(-4*math.pi,0.5,weight=1.0),
    )

def initPot():
    return combinePotentials(
        #freeParticle(),
        harmonicPotential(0.5,0.01),
    )

if __name__=='__main__':
    #
    print('Init')
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
