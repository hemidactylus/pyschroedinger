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
from twoD.interactiveSettings import (
    fullArrowKeyMap,
    patchRadii,
    fieldBevelX,
    fieldBevelY,
    potWavefunctionDampingDivider,
    potBorderWallHeight,
    potPlayerPadHeight,
    intPotentialColor,
    intPlayerColors,
)

from twoD.gui import (
    doPlot,
)

from twoD.artifacts import (
    makeRectangularArtifactList,
    makeCircleArtifact,
    makeCheckerboardRectangularArtifact,
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
    makeSmoothingMatrix,
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
            makeFakePhi(Nx,Ny,c=(0.75,0.75),ph0=(-5,5),sigma2=(0.002,0.002),weight=1),
        ],
        deltaLambdaXY=deltaLambdaX*deltaLambdaY,
    )
    return phi

def initPot(patchPosList,prevPot):
    patchPotList=[
        ellipticHolePotential(
            Nx,
            Ny,
            pPos=patchPos,
            pRadius=(0.1,0.1),
            pThickness=0.01,
            vIn=potPlayerPadHeight,
            vOut=0,
        )
        for patchPos in patchPosList
    ]
    return combinePotentials(
        [
            prevPot,
        ]+patchPotList, 
    ), patchPotList

def fixPatch(pp,ps,rdii,bbox):
    nPos=[pp[0]+ps[0],pp[1]+ps[1]]
    if nPos[0]-rdii[0]<bbox[0]:
        nPos[0]=bbox[0]+rdii[0]
    if nPos[0]+rdii[0]>bbox[2]:
        nPos[0]=bbox[2]-rdii[0]
    if nPos[1]-rdii[1]<bbox[1]:
        nPos[1]=bbox[1]+rdii[1]
    if nPos[1]+rdii[1]>bbox[3]:
        nPos[1]=bbox[3]-rdii[1]
    return tuple(nPos)

def preparePlayerInfo(nPlayers):
    if nPlayers==1:
        return {
            0: {
                'bbox': [
                    fieldBevelX,
                    fieldBevelY,
                    1-fieldBevelX,
                    1-fieldBevelY,
                ],
                'patchInitPos': (0.5,0.5),
            },
        }
    elif nPlayers==2:
        return {
            0: {
                'bbox': [
                    fieldBevelX,
                    fieldBevelY,
                    1-fieldBevelX,
                    0.5,
                ],
                'patchInitPos': (0.5,0.25),
            },
            1: {
                'bbox': [
                    fieldBevelX,
                    0.5,
                    1-fieldBevelX,
                    1-fieldBevelY,
                ],
                'patchInitPos': (0.5,0.75),
            },
        }
    else:
        raise ValueError('nPlayers cannot be %i' % nPlayers)

if __name__=='__main__':

    nPlayers=2
    playerInfo=preparePlayerInfo(nPlayers)

    arrowKeyMap={
        k: v
        for k,v in fullArrowKeyMap.items()
        if v['player']<nPlayers
    }

    # preparation of tools
    basePot=rectangularHolePotential(
        Nx,
        Ny,
        pPos=(0.0,0.0,1.,1.),
        pThickness=(0.0001,0.0001),
        vIn=0,
        vOut=potBorderWallHeight,
    )
    pot,patchPotList=initPot(
        patchPosList=[
            plInfo['patchInitPos']
            for plInfo in playerInfo.values()
        ],
        prevPot=basePot,
    )
    for plIndex,plInfo in playerInfo.items():
        plInfo['pad']=makeCircleArtifact(
            Nx=Nx,
            Ny=Ny,
            centerX=0.5,
            centerY=0.5,
            radiusX=patchRadii[0],
            radiusY=patchRadii[1],
            color=254-plIndex,
            transparentKey=0,
        )
        plInfo['patchPos']=plInfo['patchInitPos']

    phiSmoothingMatrix=makeSmoothingMatrix(
        wfSizeX=Nx,
        wfSizeY=Ny,
        periodicBCX=periodicBCX,
        periodicBCY=periodicBCY,
        smoothingMap=[
            (( 0, 0),1.0),
            (( 0,+1),0.1),
            (( 0,-1),0.1),
            ((+1, 0),0.1),
            ((-1, 0),0.1),
        ]
    )

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
        exactEnergy=True,
    )

    phi=initPhi()
    tau=0
    # in this way 255=pot, 254=player0, 253=player1
    replotting=doPlot(phi,specialColors=intPlayerColors+[intPotentialColor])

    # some info
    phLenX,phLenY=toLength_fm(LambdaX),toLength_fm(LambdaY)
    print('Lengths: LX=%4.3E, LY=%4.3E' % (phLenX,phLenY))

    plotTarget=0
    hidePot=True

    halfField=makeCheckerboardRectangularArtifact(
        Nx=Nx,
        Ny=Ny,
        posX=0.03,
        posY=0.5-0.5*0.03,
        widthX=0.94,
        heightY=0.03,
        color=255,
        transparentKey=0,
    )

    frameArtifacts=makeRectangularArtifactList(
        Nx=Nx,
        Ny=Ny,
        posX=fieldBevelX,
        posY=fieldBevelY,
        color=255,
        transparentKey=0,
    )

    initTime=time.time()
    phi,initEnergy,_,_,_=integrator.integrate(phi)
    initEnergyThreshold=(initEnergy-0.05*abs(initEnergy))
    for i in count():
        if plotTarget==0:
            phi,energy,eComp,normDev,tauIncr=integrator.integrate(phi)
            tau+=tauIncr
            #
            for plInfo in playerInfo.values():
                plInfo['pad']['pos']=(
                    int((plInfo['patchPos'][0])*Nx),
                    int((plInfo['patchPos'][1])*Nx),
                )
            # smoothing step
            if energy < initEnergyThreshold:
                phi=phiSmoothingMatrix.dot(phi)
            # damping step TEMP SLOW
            phi=phi*(np.exp(-pot/potWavefunctionDampingDivider))
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
                    plInfo['pad']
                    for plInfo in playerInfo.values()
                ]+frameArtifacts+[
                    halfField
                ],
                keysToCatch=arrowKeyMap.keys(),
            )
        else:
            doPlot(
                pot.astype(complex) if plotTarget==1 else basePot.astype(complex),
                replotting,
                title='Potential (p to switch)' if plotTarget==1 else 'BasePot (p to switch)',
                palette=1,
            )
            time.sleep(0.1)
        #
        while replotting['keyqueue']:
            tkey=replotting['keyqueue'].pop(0)
            if tkey=='p':
                plotTarget=(1+plotTarget)%3
            elif tkey=='q':
                sys.exit()
            elif tkey=='o':
                hidePot=not hidePot
            else: # arrow key
                targetPlayer=arrowKeyMap[tkey]['player']
                playerInfo[targetPlayer]['patchPos']=fixPatch(
                    playerInfo[targetPlayer]['patchPos'],
                    arrowKeyMap[tkey]['incr'],
                    patchRadii,
                    playerInfo[targetPlayer]['bbox'],
                )
        pot,patchPotList=initPot(
            patchPosList=[
                plInfo['patchPos']
                for plInfo in playerInfo.values()
            ],
            prevPot=basePot,
        )
        integrator.setPotential(pot)
