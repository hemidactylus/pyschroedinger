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
    xSize,
    xSteps,
    deltaT,
    hbar,
    m,
    periodicBC,
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
        # wGaussian(0.6,0.1,1.0),
        # wGaussianPacket(0.45,0.1,5*math.PI,0.5),
        wPlaneWave(10*math.pi,0.5)
    )

def initPot():
    return combinePotentials(
        freeParticle(),
        # harmonicPotential(0.5,0.000001),
    )

if __name__=='__main__':
    #
    print('Init')
    #
    xvalues=list(range(xSteps))
    psi=initPsi()
    pot=initPot()
    #
    replottable=doPlot(xvalues,psi,pot)
    #
    for i in itertools.count():
        for k in range(drawFreq):
            psi,normDev=integrate(psi,pot,deltaT)
        doPlot(xvalues,psi,pot,'t=%8.4f, normdev %8.4f' % (i*drawFreq*deltaT,normDev), replottable)
