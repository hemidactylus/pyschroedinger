'''
    stateMachine.py : this handles the abstract
    game state machine and its transitions.
'''

import time

from utils.units import (
    toLength_fm,
    toTime_fs,
    toEnergy_MeV,
    toMass_MeV_overC2,
)

from qpong.interactiveSettings import (
    debugSleepTime,
)

from qpong.interactive import (
    # initPhi,
    # assemblePotentials,
    # fixCursorPosition,
    # preparePlayerInfo,
    # scorePosition,
    prepareBasePotential,
    initPatchPotential,
    prepareMatrixRepository,
)

from qpong.artifacts import (
    makeRectangularArtifactList,
    makeCheckerboardRectangularArtifact,
    makeFilledBlockArtifact,
)

from twoD.dynamics import (
    # VariablePotSparseRK4Integrator,
    makeSmoothingMatrix,
)

from qpong.interactiveSettings import (
    # fullArrowKeyMap,
    # patchRadii,
    fieldBevelX,
    fieldBevelY,
    # intPotentialColor,
    # intPlayerColors,
    # winningFraction,
    # panelHeight,
    useMRepo,
    matchCountdownSteps,
    matchCountdownSpan,
)

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

gameStates={
    'still': {
        'name': 'still',
        'integrate': False,
        'displaywf': False,
        'keysToSend': {'g','i','1','2'},
        'sleep': 0.05,
        'moveCursors': False,
        'limitFrameRate': False,
    },
    'play': {
        'name': 'play',
        'integrate': True,
        'displaywf': True,
        'keysToSend': {'i', ' '},
        'sleep': debugSleepTime,
        'moveCursors': True,
        'limitFrameRate': True,
    },
    'paused': {
        'name': 'paused',
        'integrate': False,
        'displaywf': True,
        'keysToSend': {'i', ' '},
        'sleep': 0.05,
        'moveCursors': False,
        'limitFrameRate': False,
    },
    'quitting': {
        'name': 'quitting',
        'integrate': False,
        'displaywf': False,
        'keysToSend': {'y','n'},
        'sleep': 0.05,
        'moveCursors': False,
        'limitFrameRate': False,
    },
    'prestarting': {
        'name': 'prestarting',
        'integrate': False,
        'displaywf': False,
        'keysToSend': {},
        'sleep': 0.01,
        'moveCursors': False,
        'limitFrameRate': False,
    },
    'starting': {
        'name': 'starting',
        'integrate': False,
        'displaywf': True,
        'keysToSend': {},
        'sleep': 0.05,
        'moveCursors': False,
        'limitFrameRate': False,
    },
}

def initState():
    return gameStates['still']

def handleStateUpdate(curState, scEvent, mutableGameState):
    '''
        scEvent=(type,item), such as:
            ('key','p')
            ('action','start') ?
        etc

        Returns a triple (new_state,list_of_actions_to_perform, newMutableGameState)
    '''
    newState=None
    actions=[]
    if curState['name']=='still':
        if scEvent==('action','start'):
            newState=gameStates['play']
            actions.append('initPlay')
        elif scEvent[0]=='key':
            if scEvent[1]=='i':
                newState=gameStates['quitting']
            elif scEvent[1]=='g':
                newState=gameStates['prestarting']
                actions.append('initMatch')
            elif scEvent[1]=='1':
                mutableGameState['nPlayers']=1
            elif scEvent[1]=='2':
                mutableGameState['nPlayers']=2
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
                actions.append('pause')
            else:
                raise NotImplementedError
        elif scEvent[0]=='ticker':
            spf=mutableGameState['currentIntegrate']-mutableGameState['prevIntegrate']
            print('FrameRate = %.4f frames/s' % (
                1/spf if spf>0 else 0
            ))
            print('%.4f    %.4f\n' % (
                mutableGameState['prevIntegrate'],
                mutableGameState['currentIntegrate'],
            ))
            pass
        else:
            raise NotImplementedError
    elif curState['name']=='paused':
        if scEvent[0]=='key':
            if scEvent[1]=='i':
                newState=gameStates['still']
            elif scEvent[1]==' ':
                newState=gameStates['play']
                actions.append('unpause')
            else:
                raise NotImplementedError
        elif scEvent[0]=='ticker':
            pass
        else:
            raise NotImplementedError
    elif curState['name']=='quitting':
        if scEvent[0]=='key':
            if scEvent[1]=='y':
                actions.append('quitGame')
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
            pass
            newState=gameStates['starting']
        else:
            raise NotImplementedError
    elif curState['name']=='starting':
        if scEvent[0]=='ticker':
            elapsed=mutableGameState['currentTime']-mutableGameState['stateInitTime']
            if elapsed>= matchCountdownSteps*matchCountdownSpan:
                newState=gameStates['play']
                actions.append('startPlay')
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
        if newState['name']=='play':
            mutableGameState['currentIntegrate']=time.time()
            mutableGameState['prevIntegrate']=mutableGameState['currentIntegrate']
    else:
        newState=curState

    (
        mutableGameState['panelInfo'],
        mutableGameState['screenInfo'],
    )=calculatePanelInfo(newState,mutableGameState)

    return newState,actions,mutableGameState

def calculatePanelInfo(gState,mState):
    pnlInfo=None
    scnInfo=None
    if gState['name']=='paused':
        pnlInfo=[
            '',
            '  (Field size: %.2E * %.2E fm^2)' % (
                mState['physics']['phLenX'],
                mState['physics']['phLenY'],
            ),
            '  (Particle mass: %.2E MeV/c^2)' % (
                toMass_MeV_overC2(Mu),
            ),
        ]
        scnInfo=[
            ('Paused',True)
        ]
    elif gState['name']=='still':
        pnlInfo=[
            '',
            '    Welcome to Quantum Pong.',
        ]
        scnInfo=[
            ('Quantum',True),
            ('Pong',True),
            ('Press "g" to start a game',False),
            ('',False),
            ('Press "1"/"2" to change number of players',False),
            ('(currently: %i players)' % mState['nPlayers'],False),
            ('',False),
            ('Press "i" to quit/interrupt match',False),
            ('Press spacebar to pause match',False),
            ('Arrows and "a/w/s/d" move the pads',False),
        ]
    elif gState['name']=='play':
        if 'iteration' in mState:
            pnlInfo=[
                '',
                '  Time elapsed: %.3E femtoseconds' % (
                    toTime_fs(mState['physics']['tau']),
                ),
            ]
            scnInfo=[]
        else:
            pnlInfo=[
                '    About to start',
                '          ...',
            ]
    elif gState['name']=='quitting':
        pnlInfo=[
            '',
            '    Quitting game'
        ]
        scnInfo=[
            ('Quit',True),
            ('game?',True),
            ('(y/n)',True),
        ]
    elif gState['name']=='prestarting':
        pnlInfo=[
            '',
            '    Initializing ...'
        ]
    elif gState['name']=='starting':
        pnlInfo=[
            '',
            '    Ready?'
        ]
        timeStep=(mState['currentTime']-mState['stateInitTime']) /\
                (matchCountdownSpan)
        ctDisplay=max(1,matchCountdownSteps-int(timeStep))
        scnInfo=[
            ('%i' % ctDisplay,True),
        ]
    else:
        raise NotImplementedError

    return pnlInfo,scnInfo


def initMutableGameState(gState):
    '''
        initializes the big structure, containing
        all mutable game state features, to be later
        passed around
    '''
    tNow=time.time()
    mutableGameState={
        'currentTime': tNow,
        'stateInitTime': tNow,
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
        'physics': {}
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
