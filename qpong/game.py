#!/usr/bin/env python

'''
    qpong.py :
      a two-dimensional quantum pong game
'''

from itertools import count
import time
import numpy as np

from qpong.settings import (
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
    patchRadii,
    fieldBevelX,
    fieldBevelY,
    intPotentialColor,
    intPlayerColors,
    winningFraction,
    panelHeight,
    defaultSoundActive,
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
)

from qpong.stateMachine import (
    initState,
    updateWinningInfo,
    handleStateUpdate,
    initMutableGameState,
)

from Sounder import Sounder

if __name__=='__main__':

    snd=Sounder(defaultSoundActive)
    gameState=initState()
    mutableGameState=initMutableGameState(
        gameState,
        {
            'sounder': snd,
            'active': defaultSoundActive,
        }
    )
    minPlaySleepTime=1.0/maxFrameRate

    gameState,mutableGameState=handleStateUpdate(
        gameState,
        ('injectAction',('music','menu')),
        mutableGameState,
    )

    replotting=doPlot(
        None,
        # with this choice of color palette: 255=pot, 254=player0, 253=player1
        specialColors=intPlayerColors+[intPotentialColor],
        panelHeight=panelHeight,
        panelInfo=mutableGameState['panelInfo'],
        screenInfo=mutableGameState['screenInfo'],
    )

    while True:
        loopStartTime=time.time()
        # maxFrameRate
        if gameState['limitFrameRate'] and gameState['integrate']:
            fSleepTime=max(
                gameState['sleep'],
                minPlaySleepTime-mutableGameState['integrateTime'],
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
            mutableGameState['prevFrameDrawTime']=mutableGameState['lastFrameDrawTime']
            mutableGameState['lastFrameDrawTime']=time.time()
            #
            mutableGameState['iteration']+=1
            mutableGameState['physics']['tau']+=mutableGameState['physics']['tauIncr']
            scorePos=scorePosition(mutableGameState['physics']['normMap'])
            if mutableGameState['lastWinningSpree']['winner']!=None:
                scorePos=[+1.0,0.0]\
                    [mutableGameState['lastWinningSpree']['winner']]
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
                gameState,mutableGameState=updateWinningInfo(gameState,mutableGameState)

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
        gameState,mutableGameState=handleStateUpdate(
            gameState,
            ('ticker',0),
            mutableGameState,
        )
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
                gameState,mutableGameState=handleStateUpdate(
                    gameState,
                    ('key',tkey),
                    mutableGameState,
                )

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
            mutableGameState['integrateTime']=time.time()-loopStartTime
