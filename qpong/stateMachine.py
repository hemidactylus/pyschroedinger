'''
    stateMachine.py : this handles the abstract
    game state machine and its transitions.
'''

from utils.units import (
    # toLength_fm,
    toTime_fs,
    toEnergy_MeV,
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
    },
    'play': {
        'name': 'play',
        'integrate': True,
        'displaywf': True,
        'keysToSend': {'i', ' '},
        'sleep': debugSleepTime,
        'moveCursors': True,
    },
    'paused': {
        'name': 'paused',
        'integrate': False,
        'displaywf': True,
        'keysToSend': {'i', ' '},
        'sleep': 0.05,
        'moveCursors': False,
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
    newState=curState
    actions=[]
    if curState['name']=='still':
        if scEvent==('action','start'):
            newState=gameStates['play']
            actions.append('initPlay')
        elif scEvent[0]=='key':
            print('PRESSED <%s>' % scEvent[1])
            if scEvent[1]=='i':
                actions.append('quitGame')
            elif scEvent[1]=='g':
                newState=gameStates['play']
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
            print('PRESSED <%s>' % scEvent[1])
            if scEvent[1]=='i':
                newState=gameStates['still']
            elif scEvent[1]==' ':
                print('SHOULD PAUSE')
                newState=gameStates['paused']
            else:
                raise NotImplementedError
        elif scEvent[0]=='ticker':
            pass
        else:
            raise NotImplementedError
    elif curState['name']=='paused':
        if scEvent[0]=='key':
            if scEvent[1]=='i':
                newState=gameStates['still']
            elif scEvent[1]==' ':
                newState=gameStates['play']
            else:
                raise NotImplementedError
        elif scEvent[0]=='ticker':
            pass
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError

    mutableGameState['panelInfo']=calculatePanelInfo(newState,mutableGameState)

    return newState,actions,mutableGameState

def calculatePanelInfo(gState,mState):
    if gState['name']=='paused':
        return ['PAUSED']
    elif gState['name']=='still':
        return [
            'Welcome to Quantum Pong.',
            'Press G to start a game, I to quit.',
            'Switch Nplayers with "1", "2". (now: %i)' % mState['nPlayers'],
        ]
    elif gState['name']=='play':
        if 'iteration' in mState:
            return [
                'Iter %04i, t=%.1E fs' % (
                    mState['iteration'],
                    toTime_fs(mState['physics']['tau']),
                ),
                'E=%.1E MeV (%.1f)' % (
                    toEnergy_MeV(mState['physics']['energy']),
                    mState['physics']['eComp'],
                ),
                'nDev=%.2E' % (
                    mState['physics']['normDev'],
                ),
            ]
        else:
            return [
                'About to start',
                '      ...',
            ]
    else:
        raise NotImplementedError


def initMutableGameState(gState):
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
        'physics': {}
    }
    mutableGameState['panelInfo']=calculatePanelInfo(
        gState,
        mutableGameState,
    )
    return mutableGameState
