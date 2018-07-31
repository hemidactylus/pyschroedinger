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
    LambdaX,
    LambdaY,
)

from qpong.interactiveSettings import (
    # fullArrowKeyMap,
    patchRadii,
    fieldBevelX,
    fieldBevelY,
    intPotentialColor,
    intPlayerColors,
    winningFraction,
    panelHeight,
    # useMRepo,
    maxFrameRate,
)

from qpong.gui import (
    doPlot,
)

from qpong.interactive import (
    initPhi,
    assemblePotentials,
    fixCursorPosition,
    preparePlayerInfo,
    scorePosition,
    initialiseMatch,
#     prepareBasePotential,
#     initPatchPotential,
#     prepareMatrixRepository,
)

from qpong.stateMachine import (
    initState,
    handleStateUpdate,
    # calculatePanelInfo,
    initMutableGameState,
)

def performActions(actionsToPerform,mutableGameState):
    for ac in actionsToPerform:
        if ac=='initMatch':
            mutableGameState=initialiseMatch(mutableGameState)
            for scM in mutableGameState['scoreMarkers']:
                scM['visible']=False
        elif ac=='startPlay':
            for scM in mutableGameState['scoreMarkers']:
                scM['visible']=True
        elif ac=='quitGame':
            sys.exit()
        elif ac=='pause':
            for pInfo in mutableGameState['playerInfo'].values():
                pInfo['pad']['visible']=False
            for scM in mutableGameState['scoreMarkers']:
                scM['visible']=False
        elif ac=='unpause':
            for pInfo in mutableGameState['playerInfo'].values():
                pInfo['pad']['visible']=True
            for scM in mutableGameState['scoreMarkers']:
                scM['visible']=True
        else:
            raise ValueError('Unknown action "%s"' % ac)

if __name__=='__main__':

    gameState=initState()
    mutableGameState=initMutableGameState(gameState)
    minPlaySleepTime=1.0/maxFrameRate

    replotting=doPlot(
        None,
        # with this choice of color palette: 255=pot, 254=player0, 253=player1
        specialColors=intPlayerColors+[intPotentialColor],
        panelHeight=panelHeight,
        panelInfo=mutableGameState['panelInfo'],
        screenInfo=mutableGameState['screenInfo'],
    )

    while True:
        # maxFrameRate
        if gameState['limitFrameRate']:
            fSleepTime=max(
                gameState['sleep'],
                minPlaySleepTime-(
                    mutableGameState['currentIntegrate']-mutableGameState['prevIntegrate']
                ),
            )
        else:
            fSleepTime=gameState['sleep']
        time.sleep(fSleepTime)
        #
        if gameState['integrate']:
            (
                mutableGameState['physics']['phi'],
                mutableGameState['physics']['energy'],
                mutableGameState['physics']['eComp'],
                mutableGameState['physics']['normDev'],
                mutableGameState['physics']['tauIncr'],
                mutableGameState['physics']['normMap'],
            )=mutableGameState['physics']['integrator'].integrate(mutableGameState['physics']['phi'])
            #
            mutableGameState['prevIntegrate']=mutableGameState['currentIntegrate']
            mutableGameState['currentIntegrate']=time.time()
            print(mutableGameState['currentIntegrate']-mutableGameState['prevIntegrate'])
            print('***')
            #
            mutableGameState['iteration']+=1
            mutableGameState['physics']['tau']+=mutableGameState['physics']['tauIncr']
            scorePos=scorePosition(mutableGameState['physics']['normMap'])
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
                    i: mutableGameState['physics']['normMap'][3*i]
                    for i in range(mutableGameState['nPlayers'])
                    if mutableGameState['physics']['normMap'][3*i]>=winningFraction
                }
                if len(aboveThreshold)>0:
                    winner=max(aboveThreshold.items(),key=lambda kf: kf[1])[0]
                    print(' *** [%9i] Player %i scored a point! ***' % (
                        mutableGameState['iteration'],
                        winner
                    ))
            # here we make the real-valued position info into pixel integer values
            for plInfo in mutableGameState['playerInfo'].values():
                plInfo['pad']['pos']=(
                    int((plInfo['patchPos'][0])*Nx),
                    int((plInfo['patchPos'][1])*Nx),
                )
            # smoothing step
            if mutableGameState['physics']['energy'] < mutableGameState['physics']['initEnergyThreshold']:
                # this does not seem to be doable in-place (why?)
                mutableGameState['physics']['phi']=mutableGameState['phiSmoothingMatrix'].dot(
                    mutableGameState['physics']['phi']
                )
            # potential-induced damping step, in-place
            mutableGameState['physics']['phi']*=mutableGameState['physics']['damping']

        if gameState['displaywf']:
            doPlot(
                mutableGameState['physics']['phi'],
                replotting,
                artifacts=[
                    plInfo['pad']
                    for plInfo in mutableGameState['playerInfo'].values()
                ]+mutableGameState['frameArtifacts']+[
                    mutableGameState['halfField']
                ]+mutableGameState['scoreMarkers'],
                keysToCatch=mutableGameState['arrowKeyMap'].keys(),
                keysToSend=gameState['keysToSend'],
                panelInfo=mutableGameState['panelInfo'],
                screenInfo=mutableGameState['screenInfo'],
            )
        else: # some other static screen
            doPlot(
                None,
                replotting,
                panelInfo=mutableGameState['panelInfo'],
                screenInfo=mutableGameState['screenInfo'],
                keysToSend=gameState['keysToSend'],
            )
        #
        gameState,actionsToPerform,mutableGameState=handleStateUpdate(
            gameState,
            ('ticker',0),
            mutableGameState,
        )
        performActions(actionsToPerform,mutableGameState)
        while replotting['keyqueue']:
            tkey=replotting['keyqueue'].pop(0)
            if tkey in mutableGameState['arrowKeyMap']: # arrow key
                if gameState['moveCursors']:
                    targetPlayer=mutableGameState['arrowKeyMap'][tkey]['player']
                    mutableGameState['playerInfo'][targetPlayer]['patchPos']=fixCursorPosition(
                        mutableGameState['playerInfo'][targetPlayer]['patchPos'],
                        mutableGameState['arrowKeyMap'][tkey]['incr'],
                        patchRadii,
                        mutableGameState['playerInfo'][targetPlayer]['bbox'],
                    )
            else:
                gameState,actionsToPerform,mutableGameState=handleStateUpdate(
                    gameState,
                    ('key',tkey),
                    mutableGameState,
                )
                performActions(actionsToPerform,mutableGameState)

        if gameState['integrate']:
            (
                mutableGameState['physics']['pot'],
                mutableGameState['physics']['damping'],
            )=assemblePotentials(
                patchPosList=[
                    plInfo['patchPos']
                    for plInfo in mutableGameState['playerInfo'].values()
                ],
                patchPot=mutableGameState['patchPot'],
                backgroundPot=mutableGameState['basePot'],
                matrixRepo=mutableGameState['globalMatrixRepo'],
            )
            mutableGameState['physics']['integrator'].setPotential(mutableGameState['physics']['pot'])
