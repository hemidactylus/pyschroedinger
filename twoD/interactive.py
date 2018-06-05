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
    framesToDraw,
    arrowKeyMap,
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
    ellipticHolePotential,
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
    VariablePotSparseRK4Integrator,
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
            makeFakePhi(Nx,Ny,c=(0.25,0.25),ph0=(-5,5),sigma2=(0.002,0.002),weight=1),
        ],
        deltaLambdaXY=deltaLambdaX*deltaLambdaY,
    )
    return phi

def initPot(patchPos):
    return combinePotentials(
        [
            freeParticlePotential(Nx,Ny),
            # 1. an arena within a box...
            rectangularHolePotential(
                Nx,
                Ny,
                pPos=(0.03,0.03,0.94,0.94),
                pThickness=(0.00001,0.00001),
                vIn=0,
                vOut=8000,
            ),
            # rectangularHolePotential(
            #     Nx,
            #     Ny,
            #     pPos=(0.02,0.45,0.96,0.1),
            #     pThickness=(0.00001,0.0006),
            #     vIn=5000,
            #     vOut=0,
            # ),
            ellipticHolePotential(
                Nx,
                Ny,
                pPos=patchPos,
                pRadius=(0.1,0.1),
                pThickness=0.001,
                vIn=8000,
                vOut=0,
            )
        ]
    )

def fixPatch(pp,ps):
    nPos=[pp[0]+ps[0],pp[1]+ps[1]]
    if nPos[0]<0:
        nPos[0]=0
    if nPos[0]>1:
        nPos[0]=1
    if nPos[1]<0:
        nPos[1]=0
    if nPos[1]>1:
        nPos[1]=1
    return tuple(nPos)

if __name__=='__main__':

    patchPos=(0.5,0.5)

    pot=initPot(patchPos=patchPos)
    integrator=VariablePotSparseRK4Integrator(
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
    hidePot=False

    import pygame.surface
    art1=pygame.surface.Surface((4,4),0,8)
    art1.set_at((0,0),255)
    art1.set_at((0,3),255)
    art1.set_at((3,0),255)
    art1.set_at((3,3),255)
    art1.set_colorkey(0)

    art2=pygame.surface.Surface((1,Ny),0,8)
    art2.fill(255)
    art3=pygame.surface.Surface((Nx,1),0,8)
    art3.fill(255)

    initTime=time.time()
    for i in count() if framesToDraw is None else range(framesToDraw):
        if plotTarget==0:
            phi,energy,eComp,normDev,tauIncr=integrator.integrate(phi)
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
                potential=None if hidePot else pot,
                artifacts=[
                    (
                        art1,
                        (int(patchPos[0]*Nx),int(patchPos[1]*Ny)),
                    ),
                    (art2,(10,0)),
                    (art2,(Nx-10,0)),
                    (art3,(0,10)),
                    (art3,(0,Ny-10)),
                ],
            )
        else:
            doPlot(pot.astype(complex),replotting,title='Potential (p to resume)',palette=1)
            time.sleep(0.1)
        #
        while replotting['keyqueue']:
            tkey=replotting['keyqueue'].pop(0)
            if tkey=='p':
                plotTarget=1-plotTarget
            elif tkey=='q':
                sys.exit()
            elif tkey=='s':
                hidePot=not hidePot
            else: # arrow key
                # print('chg Pot',end='')
                patchPos=fixPatch(patchPos,arrowKeyMap[tkey])
                # print(' => %s' % str(patchPos))
        pot=initPot(patchPos=patchPos)
        integrator.setPotential(pot)
        #
    elapsed=time.time()-initTime
    print('Elapsed: %.2f seconds = %.3f iters/s' % (
        elapsed,
        framesToDraw/elapsed,
    ))
