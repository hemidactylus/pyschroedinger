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
    waveNumber0,
    periodicBCX,
    periodicBCY,
    drawFreq,
    LambdaX,
    LambdaY,
    framesToDraw,
)

from twoD.gui import (
    doPlot,
)

from twoD.wfunctions import (
    wavePacket,
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
    SparseMatrixRK4Integrator,
)

from utils.units import (
    toLength_fm,
    toTime_fs,
    toEnergy_MeV,
)

import numpy as np

def initPhi():
    # very fake for now
    phi=combineWFunctions(
        [
            # 1. some interference
            wavePacket(Nx,Ny,c=(0.25,0.25),ph0=(0,0),sigma2=(0.002,0.002),
                waveNumber0=waveNumber0,deltaLambdaX=deltaLambdaX,
                deltaLambdaY=deltaLambdaY,weight=1),
            # wavePacket(Nx,Ny,c=(0.75,0.5),ph0=(-5,0),sigma2=(0.004,0.004),
            #     waveNumber0=waveNumber0,deltaLambdaX=deltaLambdaX,
            #     deltaLambdaY=deltaLambdaY,weight=1),
            # wavePacket(Nx,Ny,c=(0.5,0.2),ph0=(0,+3),sigma2=(0.001,0.001),
            #     waveNumber0=waveNumber0,deltaLambdaX=deltaLambdaX,
            #     deltaLambdaY=deltaLambdaY,weight=0.8),
            # wavePacket(Nx,Ny,c=(0.5,0.8),ph0=(0,-3),sigma2=(0.001,0.001),
            #     waveNumber0=waveNumber0,deltaLambdaX=deltaLambdaX,
            #     deltaLambdaY=deltaLambdaY,weight=0.8),

            # 2. a "plane wave"
            # wavePacket(Nx,Ny,c=(0.9,0.5),ph0=(8,0),sigma2=(0.001,0.1),
            #     waveNumber0=waveNumber0,deltaLambdaX=deltaLambdaX,
            #     deltaLambdaY=deltaLambdaY,weight=0.8),
        ],
        deltaLambdaXY=deltaLambdaX*deltaLambdaY,
    )
    return phi

def initPot():
    return combinePotentials(
        [
            freeParticlePotential(Nx,Ny),
            # 1. an arena within a box
            rectangularHolePotential(
                Nx,
                Ny,
                pPos=(0.1,0.1,0.8,0.8),
                pThickness=(0.0004,0.0004),
                vIn=0,
                vOut=6000,
            ),
            rectangularHolePotential(
                Nx,
                Ny,
                pPos=(0.4,0.4,0.2,0.2),
                pThickness=(0.0004,0.0004),
                vIn=6000,
                vOut=0,
            ),
            # 2. a "double slit" for 2. Better with fixed BC
            # rectangularHolePotential(
            #     Nx,
            #     Ny,
            #     pPos=(0.5,0.0,0.02,0.4),
            #     pThickness=(0.00004,0.00004),
            #     vIn=5000,
            #     vOut=0,
            # ),
            # rectangularHolePotential(
            #     Nx,
            #     Ny,
            #     pPos=(0.5,0.46,0.02,0.08),
            #     pThickness=(0.00004,0.00004),
            #     vIn=5000,
            #     vOut=0,
            # ),
            # rectangularHolePotential(
            #     Nx,
            #     Ny,
            #     pPos=(0.5,0.6,0.02,0.4),
            #     pThickness=(0.00004,0.00004),
            #     vIn=5000,
            #     vOut=0,
            # ),
        ]
    )

if __name__=='__main__':

    pot=initPot()
    integrator=SparseMatrixRK4Integrator(
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

    plotTarget=0

    keysToSend={'i','p'}

    initTime=time.time()
    for i in count() if framesToDraw is None else range(framesToDraw):
        if plotTarget==0:
            phi,energy,eComp,normDev,tauIncr,_=integrator.integrate(phi)
            tau+=tauIncr
            doPlot(
                phi,
                replotting,
                title='Iter %04i, t=%.1E fs, E=%.1E MeV (%.1f), nDev=%.2E' % (
                    i,
                    toTime_fs(tau),
                    toEnergy_MeV(energy),
                    eComp,
                    normDev,
                ),
                palette=0,
                keysToSend=keysToSend,
            )
        else:
            doPlot(pot.astype(complex),replotting,title='Potential (p to resume)',palette=1,keysToSend=keysToSend)
            time.sleep(0.1)
        #
        while replotting['keyqueue']:
            tkey=replotting['keyqueue'].pop(0)
            if tkey=='p':
                plotTarget=1-plotTarget
            elif tkey=='i':
                sys.exit()
        #
    elapsed=time.time()-initTime
    print('Elapsed: %.2f seconds = %.3f iters/s' % (
        elapsed,
        framesToDraw/elapsed,
    ))