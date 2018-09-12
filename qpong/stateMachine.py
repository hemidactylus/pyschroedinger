'''
    stateMachine.py : this handles the abstract
    game state machine and its transitions.
'''

import time
import sys

from utils.units import (
    toLength_fm,
)

from qpong.settings import (
    Nx,
    Ny,
    deltaTau,
    deltaLambdaX,
    deltaLambdaY,
    periodicBCX,
    periodicBCY,
    LambdaX,
    LambdaY,
)

from qpong.interactive import (
    prepareBasePotential,
    initPatchPotential,
    prepareMatrixRepository,
    scorePosition,
    calculateScorePosSector,
    getScoreSectorSound,
)

from qpong.artifacts import (
    makeRectangularArtifactList,
    makeCheckerboardRectangularArtifact,
    makeFilledBlockArtifact,
)

from twoD.dynamics import (
    makeSmoothingMatrix,
)

from qpong.interactiveSettings import (
    fieldBevelX,
    fieldBevelY,
    halfFieldArtifactWidth,
    useMRepo,
    matchCountdownSteps,
    matchCountdownSpan,
    endMatchStillTime,
    endPlayStillTime,
    winningSpreeNumIterations,
    defaultMatchesToWinAPlay,
    maximumMatchesToWinAPlay,
    winningSpreeNumIterations,
    aboutToWinDangerSignSteps,
    winningFraction,
)

from qpong.panelInfo import calculatePanelInfo
from qpong.gameStates import gameStates
from qpong.actions import performActions

def initState():
    return gameStates['still']

def handleStateUpdate(curState, scEvent, mutableGameState):
    '''
        scEvent=(type,item), such as:
            ('key','p')
            ('ticker',<dummy_value>)
        etc

        Returns 2-tuple (new_state, newMutableGameState)
    '''
    newState=None
    if curState['integrate']:
        '''
            
        '''
        mutableGameState['lastWinningSpree']['scorePos']=\
            scorePosition(mutableGameState['physics']['normMap'])
        if mutableGameState['lastWinningSpree']['winner']!=None:
            mutableGameState['lastWinningSpree']['scorePos']=[+1.0,0.0]\
                [mutableGameState['lastWinningSpree']['winner']]
        mutableGameState['lastWinningSpree']['scorePosInteger']=int(
            Nx*(fieldBevelX+mutableGameState['lastWinningSpree']['scorePos']*(1-2*fieldBevelX))
        )
        mutableGameState['scoreMarkers'][0]['offset']=(
            mutableGameState['lastWinningSpree']['scorePosInteger'],
            0,
        )
        mutableGameState['scoreMarkers'][1]['offset']=(
            mutableGameState['lastWinningSpree']['scorePosInteger'],
            0,
        )
        newPosSector=calculateScorePosSector(
            mutableGameState['lastWinningSpree']['scorePos']
        )
        if newPosSector!=mutableGameState['lastWinningSpree']['scorePosSector']:
            # enqueue sound if the transition warrants it
            newSound=getScoreSectorSound(
                mutableGameState['lastWinningSpree']['scorePosSector'],
                newPosSector,
            )
            if newSound is not None:
                mutableGameState['actionqueue'].append(('sound',newSound))
            mutableGameState['lastWinningSpree']['scorePosSector']=newPosSector
    if curState['name']=='still':
        if scEvent==('action','start'):
            newState=gameStates['play']
        elif scEvent[0]=='injectAction':
            mutableGameState['actionqueue'].append(scEvent[1])
        elif scEvent[0]=='key':
            if scEvent[1]=='i':
                newState=gameStates['quitting']
            elif scEvent[1]=='g':
                newState=gameStates['initplay']
                mutableGameState['actionqueue'].append(('markers','hide'))
                mutableGameState['actionqueue'].append(('initmatch',''))
            elif scEvent[1]=='1':
                if mutableGameState['nPlayers']!=1:
                    mutableGameState['actionqueue'].append(('sound','nplayers'))
                    mutableGameState['nPlayers']=1
            elif scEvent[1]=='2':
                if mutableGameState['nPlayers']!=2:
                    mutableGameState['actionqueue'].append(('sound','nplayers'))
                    mutableGameState['nPlayers']=2
            elif scEvent[1]=='c':
                if mutableGameState['matchesToWinPlay']>1:
                    mutableGameState['actionqueue'].append(('sound','n_matches_down'))
                    mutableGameState['matchesToWinPlay']-=1
            elif scEvent[1]=='v':
                if mutableGameState['matchesToWinPlay']<maximumMatchesToWinAPlay:
                    mutableGameState['actionqueue'].append(('sound','n_matches_up'))
                    mutableGameState['matchesToWinPlay']+=1
            elif scEvent[1]=='b':
                mutableGameState['sound']['active']=not mutableGameState['sound']['active']
                mutableGameState['sound']['sounder'].setActive(
                    mutableGameState['sound']['active']
                )
                if mutableGameState['sound']['active']:
                    mutableGameState['actionqueue'].append(('sound','sound_on'))
            elif scEvent[1]=='m':
                newState=gameStates['info']
            else:
                raise NotImplementedError
        elif scEvent[0]=='ticker':
            pass
        else:
            raise NotImplementedError
    elif curState['name']=='play':
        if scEvent[0]=='key':
            if scEvent[1]=='i':
                newState=gameStates['still']
            elif scEvent[1]==' ':
                newState=gameStates['paused']
                mutableGameState['actionqueue'].append(('pause','pause'))
            elif scEvent[1]=='b':
                mutableGameState['sound']['active']=not mutableGameState['sound']['active']
                mutableGameState['sound']['sounder'].setActive(
                    mutableGameState['sound']['active']
                )
            else:
                raise NotImplementedError
        elif scEvent[0]=='ticker':
            timeBetweenFrames=mutableGameState['lastFrameDrawTime']-mutableGameState['prevFrameDrawTime']
            mutableGameState['framerate']=1/timeBetweenFrames if timeBetweenFrames>0 else 0
        elif scEvent[0]=='matchWin':
            winner=scEvent[1]
            mutableGameState['playScores']['matchScores'].append(winner)
            playScores={k: 0 for k in range(mutableGameState['nPlayers'])}
            for mtc in mutableGameState['playScores']['matchScores']:
                playScores[mtc]+=1
            mutableGameState['playWinner']['scores']=playScores
            # did the current play finish?
            winningPlayer,winningScore=sorted(
                mutableGameState['playWinner']['scores'].items(),
                key=lambda ps: ps[1],
                reverse=True
            )[0]
            if winningScore>=mutableGameState['matchesToWinPlay']:
                mutableGameState['playWinner']['winner']=winningPlayer
                newState=gameStates['showendplay']
                #
                mutableGameState['actionqueue'].append(('sound','victory'))
            else:
                newState=gameStates['showendmatch']
                #
                mutableGameState['actionqueue'].append(('sound','matchscore'))
        else:
            raise NotImplementedError
    elif curState['name']=='paused':
        if scEvent[0]=='key':
            if scEvent[1]=='i':
                newState=gameStates['still']
            elif scEvent[1]==' ':
                newState=gameStates['play']
                mutableGameState['actionqueue'].append(('pause','unpause'))
            elif scEvent[1]=='b':
                mutableGameState['sound']['active']=not mutableGameState['sound']['active']
                mutableGameState['sound']['sounder'].setActive(
                    mutableGameState['sound']['active']
                )
            else:
                raise NotImplementedError
        elif scEvent[0]=='ticker':
            pass
        else:
            raise NotImplementedError
    elif curState['name']=='showendmatch':
        if scEvent[0]=='key':
            if scEvent[1]=='i':
                newState=gameStates['still']
            else:
                raise NotImplementedError
        elif scEvent[0]=='ticker':
            elapsed=mutableGameState['currentTime']-mutableGameState['stateInitTime']
            if elapsed>= endMatchStillTime:
                newState=gameStates['prestarting']
                mutableGameState['actionqueue'].append(('markers','hide'))
                mutableGameState['actionqueue'].append(('initmatch',''))
        else:
            raise NotImplementedError
    elif curState['name']=='showendplay':
        if scEvent[0]=='key':
            raise NotImplementedError
        elif scEvent[0]=='ticker':
            elapsed=mutableGameState['currentTime']-mutableGameState['stateInitTime']
            if elapsed>= endPlayStillTime:
                newState=gameStates['still']
                mutableGameState['actionqueue'].append(('markers','hide'))
        else:
            raise NotImplementedError
    elif curState['name']=='quitting':
        if scEvent[0]=='key':
            if scEvent[1]=='y':
                mutableGameState['actionqueue'].append(('quitgame',''))
            elif scEvent[1]=='n':
                newState=gameStates['still']
            else:
                raise NotImplementedError
        elif scEvent[0]=='ticker':
            pass
        else:
            raise NotImplementedError
    elif curState['name']=='prestarting':
        if scEvent[0]=='ticker':
            newState=gameStates['starting']
            mutableGameState['actionqueue'].append(('sound','ct_3'))
            mutableGameState['ctDisplay']=matchCountdownSteps
        else:
            raise NotImplementedError
    elif curState['name']=='initplay':
        if scEvent[0]=='ticker':
            newState=gameStates['prestarting']
            mutableGameState['actionqueue'].append(('startplay',''))
        else:
            raise NotImplementedError
    elif curState['name']=='starting':
        timeStep=(mutableGameState['currentTime']-mutableGameState['stateInitTime']) /\
                (matchCountdownSpan)
        newCtDisplay=max(1,matchCountdownSteps-int(timeStep))
        if newCtDisplay!=mutableGameState['ctDisplay']:
            mutableGameState['actionqueue'].append(('sound','ct_%i' % newCtDisplay))
            mutableGameState['ctDisplay']=newCtDisplay
        if scEvent[0]=='ticker':
            elapsed=mutableGameState['currentTime']-mutableGameState['stateInitTime']
            if elapsed>= matchCountdownSteps*matchCountdownSpan:
                mutableGameState['actionqueue'].append(('markers','show'))
                newState=gameStates['play']
        else:
            raise NotImplementedError
    elif curState['name']=='info':
        if scEvent[0]=='key':
            if scEvent[1]=='i':
                newState=gameStates['still']
            else:
                raise NotImplementedError
        elif scEvent[0]=='ticker':
            pass
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError

    # if a new state was explicitly reached
    if scEvent[0]=='ticker':
        mutableGameState['currentTime']=time.time()
    if newState is not None:
        mutableGameState['stateInitTime']=time.time()
        mutableGameState['currentTime']=mutableGameState['stateInitTime']
        #
        if newState['musicMode']!=mutableGameState['musicMode']:
            if newState['musicMode'] is None:
                mutableGameState['actionqueue'].append(('stopmusic',''))
            else:
                mutableGameState['actionqueue'].append(('music',newState['musicMode']))
        mutableGameState['musicMode']=newState['musicMode']
        #
        if newState['name']=='play':
            mutableGameState['lastFrameDrawTime']=time.time()
            mutableGameState['prevFrameDrawTime']=mutableGameState['lastFrameDrawTime']
            mutableGameState['integrateTime']=0.0
        #
        if newState['name']=='quitting':
            mutableGameState['actionqueue'].append(('sound','quit'))
    else:
        newState=curState

    mutableGameState=performActions(mutableGameState)
    (
        mutableGameState['panelInfo'],
        mutableGameState['screenInfo'],
    )=calculatePanelInfo(newState,mutableGameState)

    return newState,mutableGameState



def initMutableGameState(gState,sound):
    '''
        initializes the big structure, containing
        all mutable game state features, to be later
        passed around
    '''
    tNow=time.time()
    mutableGameState={
        'actionqueue': [],
        'sound': sound,
        'currentTime': tNow,
        'stateInitTime': tNow,
        'nPlayers': 2,
        'matchesToWinPlay': defaultMatchesToWinAPlay,
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
            posX=0.5*(1-halfFieldArtifactWidth/2),
            posY=fieldBevelY,
            widthX=halfFieldArtifactWidth,
            heightY=1-2*fieldBevelY,
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
        'physics': {},
        'musicMode': gState['musicMode'],
    }
    (
        mutableGameState['panelInfo'],
        mutableGameState['screenInfo'],
    )=calculatePanelInfo(
        gState,
        mutableGameState,
    )
    (
        mutableGameState['physics']['phLenX'],
        mutableGameState['physics']['phLenY'],
    )=toLength_fm(LambdaX),toLength_fm(LambdaY)
    return mutableGameState

def updateWinningInfo(gameState,mutableGameState):
    aboveThreshold={
        1-i: mutableGameState['physics']['normMap'][3*i]
        for i in range(mutableGameState['nPlayers'])
        if mutableGameState['physics']['normMap'][3*i]>=winningFraction
    }
    if len(aboveThreshold)>0:
        winner=max(aboveThreshold.items(),key=lambda kf: kf[1])[0]
    else:
        winner=None
    #
    if mutableGameState['lastWinningSpree']['winner']!=winner:
        mutableGameState['lastWinningSpree'].update({
            'winner': winner,
            'entered': mutableGameState['iteration'],
        })
    elif winner is not None:
        if (mutableGameState['iteration']-mutableGameState['lastWinningSpree']['entered'])>=winningSpreeNumIterations:
            gameState,mutableGameState=handleStateUpdate(
                gameState,
                ('matchWin',winner),
                mutableGameState,
            )
        else:
            spreeIterationsToGo=mutableGameState['iteration']-\
                mutableGameState['lastWinningSpree']['entered']
            mutableGameState['lastWinningSpree']['closenessFraction']=\
                1.0-float(spreeIterationsToGo)/float(winningSpreeNumIterations)
    if winner is not None:
        spreeIterationsToGo=mutableGameState['iteration']-\
            mutableGameState['lastWinningSpree']['entered']
        closenessFraction=1.0-float(spreeIterationsToGo)/float(winningSpreeNumIterations)
        mutableGameState['lastWinningSpree']['closenessFraction']=closenessFraction
        if closenessFraction<aboutToWinDangerSignSteps[0]:
            mutableGameState['lastWinningSpree']['closenessFractionStage']=2
        elif closenessFraction<aboutToWinDangerSignSteps[1]:
            mutableGameState['lastWinningSpree']['closenessFractionStage']=1
        else:
            if mutableGameState['lastWinningSpree']['closenessFractionStage']<0:
                mutableGameState['actionqueue'].append(('sound','danger'))
            mutableGameState['lastWinningSpree']['closenessFractionStage']=0
    else:
        mutableGameState['lastWinningSpree']['closenessFraction']=0.0
        mutableGameState['lastWinningSpree']['closenessFractionStage']=-1

    return gameState,mutableGameState
