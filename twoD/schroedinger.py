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
    rectangularHolePotential,
)

from twoD.tools import (
    combineWFunctions,
    combinePotentials,
    norm,
)

from twoD.dynamics import (
    NaiveFiniteDifferenceIntegrator,
    RK4StepByStepIntegrator,
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
            makeFakePhi(Nx,Ny,c=(0.25,0.5),ph0=(+5,0),sigma2=(0.004,0.004),weight=1),
            makeFakePhi(Nx,Ny,c=(0.75,0.5),ph0=(-5,0),sigma2=(0.004,0.004),weight=1),
            makeFakePhi(Nx,Ny,c=(0.5,0.2),ph0=(0,+3),sigma2=(0.001,0.001),weight=0.8),
            makeFakePhi(Nx,Ny,c=(0.5,0.8),ph0=(0,-3),sigma2=(0.001,0.001),weight=0.8),
        ],
        deltaLambdaXY=deltaLambdaX*deltaLambdaY,
    )
    return phi

def initPot():
    return combinePotentials(
        [
            freeParticlePotential(Nx,Ny),
            rectangularHolePotential(
                Nx,
                Ny,
                pPos=(0.05,0.05,0.9,0.9),
                pThickness=(0.0004,0.0004),
                vIn=0,
                vOut=2000,
            ),
            rectangularHolePotential(
                Nx,
                Ny,
                pPos=(0.4,0.4,0.2,0.2),
                pThickness=(0.0001,0.0001),
                vIn=2000,
                vOut=0,
            ),
        ]
    )

if __name__=='__main__':

    pot=initPot()
    integrator=RK4StepByStepIntegrator(
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
        #
        if replotting['keyqueue']==['p']:
            # switch to potential mode for one second
            doPlot(pot.astype(complex),title='Potential, 1 sec...')
            time.sleep(1)
            #
            replotting['keyqueue']=[]
        #