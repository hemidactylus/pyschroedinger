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
    panelHeight,
    useMRepo,
)

from qpong.gui import (
    doPlot,
)

from qpong.artifacts import (
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
    prepareMatrixRepository,
)

from qpong.stateMachine import (
    initState,
    # gameStates,
    handleStateChange,
)

def initMutableGameState():
    '''
        initializes the big structure, containing
        all mutable game state features, to be later
        passed around
    '''
    mutableGameState={
        'nPlayers': 2,
        'basePot': prepareBasePotential(),
        'patchPot': initPatchPotential(),
        'globalMatrixRepo': prepareMatrixRepository() if useMRepo else None,
        'phiSmoothingMatrix': makeSmoothingMatrix(
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
        ),
        'halfField': makeCheckerboardRectangularArtifact(
            Nx=Nx,
            Ny=Ny,
            posX=0.5-0.5*fieldBevelX,
            posY=fieldBevelX,
            widthX=fieldBevelX,
            heightY=1-2*fieldBevelX,
            color=255,
            transparentKey=0,
        ),
        'scoreMarkers': [
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
        ],
        'frameArtifacts': makeRectangularArtifactList(
            Nx=Nx,
            Ny=Ny,
            posX=fieldBevelX,
            posY=fieldBevelY,
            color=255,
            transparentKey=0,
        ),
        'arrowKeyMap':{},
    }
    return mutableGameState

if __name__=='__main__':

    mutableGameState=initMutableGameState()
    gameState=initState()

    replotting=doPlot(
        None,
        # with this choice of color palette: 255=pot, 254=player0, 253=player1
        specialColors=intPlayerColors+[intPotentialColor],
        panelHeight=panelHeight,
        panelInfo=[
            'Initialization.',
        ],
    )

    # some info
    phLenX,phLenY=toLength_fm(LambdaX),toLength_fm(LambdaY)
    print('Lengths: LX=%4.3E, LY=%4.3E' % (phLenX,phLenY))

    for i in count() if framesToDraw is None else range(framesToDraw):
        time.sleep(gameState['sleep'])
        if gameState['integrate']:
            phi,energy,eComp,normDev,tauIncr,normMap=integrator.integrate(phi)
            tau+=tauIncr
            scorePos=scorePosition(normMap)
            scorePosInteger=int(Nx*(fieldBevelX+scorePos*(1-2*fieldBevelX)))
            mutableGameState['scoreMarkers'][0]['offset']=(
                scorePosInteger,
                0,
            )
            mutableGameState['scoreMarkers'][1]['offset']=(
                scorePosInteger,
                0,
            )
            # scoring check
            if mutableGameState['nPlayers']>1:
                aboveThreshold={
                    i: normMap[3*i]
                    for i in range(mutableGameState['nPlayers'])
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
                # this does not seem to be doable in-place (why?)
                phi=mutableGameState['phiSmoothingMatrix'].dot(phi)
            # potential-induced damping step, in-place
            phi*=damping
            titleMessage=[
                'Iter %04i, t=%.1E fs' % (
                    i,
                    toTime_fs(tau),
                ),
                'E=%.1E MeV (%.1f)' % (
                    toEnergy_MeV(energy),
                    eComp,
                ),
                'nDev=%.2E' % (
                    normDev,
                ),
            ]
        if gameState['displaywf']:
            doPlot(
                phi,
                replotting,
                artifacts=[
                    plInfo['pad']
                    for plInfo in playerInfo.values()
                ]+mutableGameState['frameArtifacts']+[
                    mutableGameState['halfField']
                ]+mutableGameState['scoreMarkers'],
                keysToCatch=mutableGameState['arrowKeyMap'].keys(),
                keysToSend=gameState['keysToSend'],
                # panelHeight=panelHeight,
                panelInfo=titleMessage,
            )
        else: # some other static screen
            doPlot(
                None,
                replotting,
                # panelHeight=panelHeight,
                panelInfo=[
                    'Welcome to Quantum Pong. (%i)' % i,
                    'Press G to start a game, I to quit.',
                    'Switch Nplayers with "1", "2".',
                ],                
                keysToSend=gameState['keysToSend'],
            )
        #
        while replotting['keyqueue']:
            tkey=replotting['keyqueue'].pop(0)
            if tkey in mutableGameState['arrowKeyMap']: # arrow key
                if gameState['moveCursors']:
                    targetPlayer=mutableGameState['arrowKeyMap'][tkey]['player']
                    playerInfo[targetPlayer]['patchPos']=fixCursorPosition(
                        playerInfo[targetPlayer]['patchPos'],
                        mutableGameState['arrowKeyMap'][tkey]['incr'],
                        patchRadii,
                        playerInfo[targetPlayer]['bbox'],
                    )
            else:
                gameState,actionsToPerform,mutableGameState=handleStateChange(
                    gameState,
                    ('key',tkey),
                    mutableGameState,
                )
                for ac in actionsToPerform:
                    print('TO PERFORM %s' % str(ac))
                    if ac=='initMatch':
                        playerInfo=preparePlayerInfo(mutableGameState['nPlayers'])
                        mutableGameState['arrowKeyMap']={
                            k: v
                            for k,v in fullArrowKeyMap.items()
                            if v['player'] in playerInfo
                        }
                        pot,damping=assemblePotentials(
                            patchPosList=[
                                plInfo['patchInitPos']
                                for plInfo in playerInfo.values()
                            ],
                            patchPot=mutableGameState['patchPot'],
                            backgroundPot=mutableGameState['basePot'],
                            matrixRepo=mutableGameState['globalMatrixRepo'],
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
                        phi,initEnergy,_,_,_,_=integrator.integrate(phi)
                        initEnergyThreshold=(initEnergy-0.05*abs(initEnergy))
                    elif ac=='quitGame':
                        sys.exit()

        if gameState['integrate']:
            pot,damping=assemblePotentials(
                patchPosList=[
                    plInfo['patchPos']
                    for plInfo in playerInfo.values()
                ],
                patchPot=mutableGameState['patchPot'],
                backgroundPot=mutableGameState['basePot'],
                matrixRepo=mutableGameState['globalMatrixRepo'],
            )
            integrator.setPotential(pot)
