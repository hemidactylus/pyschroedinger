#!/usr/bin/env python

'''
    qpong.py :
      a two-dimensional quantum pong game
'''

from itertools import count
import time
import sys
import numpy as np

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
)

from qpong.interactiveSettings import (
    fullArrowKeyMap,
    patchRadii,
    fieldBevelX,
    fieldBevelY,
    intPotentialColor,
    intPlayerColors,
    winningFraction,
    debugSleepTime,
)

from twoD.gui import (
    doPlot,
)

from twoD.artifacts import (
    makeRectangularArtifactList,
    # makeCircleArtifact,
    makeCheckerboardRectangularArtifact,
    makeFilledBlockArtifact,
)

from twoD.dynamics import (
    VariablePotSparseRK4Integrator,
    makeSmoothingMatrix,
)

from utils.units import (
    toLength_fm,
    toTime_fs,
    toEnergy_MeV,
)

from qpong.interactive import (
    initPhi,
    assemblePotentials,
    fixCursorPosition,
    preparePlayerInfo,
    scorePosition,
    prepareBasePotential,
    initPatchPotential,
)

if __name__=='__main__':

    if '-1' in sys.argv[1:]:
        nPlayers=1
    else:
        nPlayers=2
    
    playerInfo=preparePlayerInfo(nPlayers)

    arrowKeyMap={
        k: v
        for k,v in fullArrowKeyMap.items()
        if v['player'] in playerInfo
    }

    # preparation of tools
    basePot=prepareBasePotential()
    patchPot=initPatchPotential()

    pot,damping=assemblePotentials(
        patchPosList=[
            plInfo['patchInitPos']
            for plInfo in playerInfo.values()
        ],
        patchPot=patchPot,
        backgroundPot=basePot,
    )

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
        slicesSet=[0.0,0.25,0.5,0.75],
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
        posX=0.5-0.5*fieldBevelX,
        posY=fieldBevelX,
        widthX=fieldBevelX,
        heightY=1-2*fieldBevelX,
        color=255,
        transparentKey=0,
    )

    # FIXME temp solution to the score marker
    scoreMarkers=[
        makeFilledBlockArtifact(
            (0,0),
            (1,3),
            color=255,
        ),
        makeFilledBlockArtifact(
            (0,Ny-3),
            (1,3),
            color=255,
        ),
    ]

    frameArtifacts=makeRectangularArtifactList(
        Nx=Nx,
        Ny=Ny,
        posX=fieldBevelX,
        posY=fieldBevelY,
        color=255,
        transparentKey=0,
    )

    keysToSend={'p','o','i'}

    initTime=time.time()
    phi,initEnergy,_,_,_,_=integrator.integrate(phi)
    initEnergyThreshold=(initEnergy-0.05*abs(initEnergy))
    for i in count() if framesToDraw is None else range(framesToDraw):
        if debugSleepTime>0:
            time.sleep(debugSleepTime)
        if plotTarget==0:
            phi,energy,eComp,normDev,tauIncr,normMap=integrator.integrate(phi)
            tau+=tauIncr

            scorePos=scorePosition(normMap)
            # TEMP fixme score markers more grafecully placed!
            scorePosInteger=int(Nx*(fieldBevelX+scorePos*(1-2*fieldBevelX)))
            scoreMarkers[0]['offset']=(
                scorePosInteger,
                0,
            )
            scoreMarkers[1]['offset']=(
                scorePosInteger,
                0,
            )
            # scoring check
            if nPlayers>1:
                aboveThreshold={
                    i: normMap[3*i]
                    for i in range(nPlayers)
                    if normMap[3*i]>=winningFraction
                }
                if len(aboveThreshold)>0:
                    winner=max(aboveThreshold.items(),key=lambda kf: kf[1])[0]
                    print(' *** [%9i] Player %i scored a point! ***' % (i,winner))
            #
            for plInfo in playerInfo.values():
                plInfo['pad']['pos']=(
                    int((plInfo['patchPos'][0])*Nx),
                    int((plInfo['patchPos'][1])*Nx),
                )

            # smoothing step
            if energy < initEnergyThreshold:
                phi=phiSmoothingMatrix.dot(phi)
            # damping step
            phi=phi*damping
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
                ]+scoreMarkers,
                keysToCatch=arrowKeyMap.keys(),
                keysToSend=keysToSend,
            )
        else:
            doPlot(
                pot.astype(complex) if plotTarget==1 else basePot.astype(complex),
                replotting,
                title='Potential (p to switch)' if plotTarget==1 else 'BasePot (p to switch)',
                palette=1,
                keysToSend=keysToSend,
            )
        #
        while replotting['keyqueue']:
            tkey=replotting['keyqueue'].pop(0)
            if tkey=='p':
                plotTarget=(1+plotTarget)%3
            elif tkey=='i':
                sys.exit()
            elif tkey=='o':
                hidePot=not hidePot
            else: # arrow key
                targetPlayer=arrowKeyMap[tkey]['player']
                playerInfo[targetPlayer]['patchPos']=fixCursorPosition(
                    playerInfo[targetPlayer]['patchPos'],
                    arrowKeyMap[tkey]['incr'],
                    patchRadii,
                    playerInfo[targetPlayer]['bbox'],
                )
        pot,damping=assemblePotentials(
            patchPosList=[
                plInfo['patchPos']
                for plInfo in playerInfo.values()
            ],
            patchPot=patchPot,
            backgroundPot=basePot,
        )
        integrator.setPotential(pot)
