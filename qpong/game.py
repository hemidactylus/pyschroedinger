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
)

from qpong.gui import (
    doPlot,
)

from utils.units import (
    toLength_fm,
    # toTime_fs,
    # toEnergy_MeV,
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
    calculatePanelInfo,
    initMutableGameState,
)

if __name__=='__main__':

    gameState=initState()
    mutableGameState=initMutableGameState(gameState)

    replotting=doPlot(
        None,
        # with this choice of color palette: 255=pot, 254=player0, 253=player1
        specialColors=intPlayerColors+[intPotentialColor],
        panelHeight=panelHeight,
        panelInfo=mutableGameState['panelInfo'],
    )

    (
        mutableGameState['physics']['phLenX'],
        mutableGameState['physics']['phLenY'],
    )=toLength_fm(LambdaX),toLength_fm(LambdaY)

    while True:
        time.sleep(gameState['sleep'])
        if gameState['integrate']:
            (
                mutableGameState['physics']['phi'],
                mutableGameState['physics']['energy'],
                mutableGameState['physics']['eComp'],
                mutableGameState['physics']['normDev'],
                mutableGameState['physics']['tauIncr'],
                mutableGameState['physics']['normMap'],
            )=mutableGameState['physics']['integrator'].integrate(mutableGameState['physics']['phi'])
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
            #
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
                # panelInfo=titleMessage,
            )
        else: # some other static screen
            doPlot(
                None,
                replotting,
                panelInfo=mutableGameState['panelInfo'],
                keysToSend=gameState['keysToSend'],
            )
        #
        gameState,actionsToPerform,mutableGameState=handleStateUpdate(
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
                gameState,actionsToPerform,mutableGameState=handleStateUpdate(
                    gameState,
                    ('key',tkey),
                    mutableGameState,
                )
                for ac in actionsToPerform:
                    print('TO PERFORM %s' % str(ac))
                    if ac=='initMatch':
                        mutableGameState=initialiseMatch(mutableGameState)
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
                        print('*** UNKNOWN ACTION TO PERFORM ***')

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
