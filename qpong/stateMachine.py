'''
    stateMachine.py : this handles the abstract
    game state machine and its transitions.
'''

from qpong.interactiveSettings import (
    debugSleepTime,
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

def handleStateChange(curState, scEvent, mutableGameState):
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
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError

    return newState,actions,mutableGameState
