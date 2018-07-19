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

def handleStateChange(curState, scEvent):
    '''
        scEvent=(type,item), such as:
            ('key','p')
            ('action','start') ?
        etc

        Returns a pair (new_state,list_of_actions_to_perform)
    '''
    if curState['name']=='still':
        if scEvent==('action','start'):
            return gameStates['play'],['initPlay']
        elif scEvent[0]=='key':
            print('PRESSED <%s>' % scEvent[1])
            if scEvent[1]=='i':
                print('SHOULD LEAVE GAME')
                return curState,['quitGame']
            elif scEvent[1]=='g':
                print('SHOULD START')
                return gameStates['play'],['initMatch']
            elif scEvent[1]=='1':
                print('SHOULD SET TO 1')
                return curState,[]
            elif scEvent[1]=='2':
                print('SHOULD SET TO 2')
                return curState,[]
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError
    elif curState['name']=='play':
        if scEvent[0]=='key':
            print('PRESSED <%s>' % scEvent[1])
            if scEvent[1]=='i':
                print('SHOULD STOP MATCH')
                return gameStates['still'],[]
            elif scEvent[1]==' ':
                print('SHOULD PAUSE')
                return gameStates['paused'],[]
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError
    elif curState['name']=='paused':
        if scEvent[0]=='key':
            print('PRESSED <%s>' % scEvent[1])
            if scEvent[1]=='i':
                print('SHOULD STOP MATCH')
                return gameStates['still'],[]
            elif scEvent[1]==' ':
                print('SHOULD UNPAUSE')
                return gameStates['play'],[]
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError
