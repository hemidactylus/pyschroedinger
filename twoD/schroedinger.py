#!/usr/bin/env python

'''
    schroedinger.py :
      two-dimensional study of integration of the
      Schroedinger equation
'''
from itertools import count
import time
import sys

from twoD.settings import (
    Nx,
    Ny,
    Mu,
    deltaTau,
    deltaLambdaX,
    deltaLambdaY,
    periodicBCX,
    periodicBCY,
    drawFreq,
    LambdaX,
    LambdaY,
)

from twoD.gui import (
    doPlot,
)

from twoD.wfunctions import (
    makeFakePhi,
)
from twoD.potentials import (
    freeParticlePotential,
)

from twoD.tools import (
    combineWFunctions,
    norm,
)

from twoD.dynamics import (
    NaiveFiniteDifferenceIntegrator,
)

from utils.units import (
    toLength_fm,
    toTime_fs,
    toEnergy_Mev,
)

import numpy as np

def initPhi():
    # very fake for now
    phi=combineWFunctions(
        [
            makeFakePhi(Nx,Ny,0.5,0.5,0.01,amplitude=0.4),
            # makeFakePhi(Nx,Ny,0.75,0.25,0.1,amplitude=0.8),
        ],
        deltaLambdaXY=deltaLambdaX*deltaLambdaY,
    )
    return phi

def initPot():
    return freeParticlePotential(Nx,Ny)

if __name__=='__main__':

    pot=initPot()
    integrator=NaiveFiniteDifferenceIntegrator(
        wfSizeX=Nx,
        wfSizeY=Ny,
        deltaTau=deltaTau,
        deltaLambdaX=deltaLambdaX,
        deltaLambdaY=deltaLambdaY,
        nIntegrationSteps=drawFreq,
        vPotential=pot,
        periodicBCX=periodicBCX,
        periodicBCY=periodicBCY,
        mu=Mu,
    )

    phi=initPhi()
    tau=0
    replotting=doPlot(phi)

    # some info
    phLenX,phLenY=toLength_fm(LambdaX),toLength_fm(LambdaY)
    print('Lengths: LX=%4.3E, LY=%4.3E' % (phLenX,phLenY))

    for i in count():
        phi,normDev,tauIncr=integrator.integrate(phi,drawFreq)
        tau+=tauIncr
        doPlot(phi,replotting,title='Iter %06i, t=%4.3E fs, nDev=%.4E' % (
            i,
            toTime_fs(tau),
            normDev,
        ))
