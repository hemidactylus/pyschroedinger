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
    },
    'play': {
        'name': 'play',
        'integrate': True,
        'displaywf': True,
        'keysToSend': {'i'},
        'sleep': debugSleepTime,
    },
}

def initState():
    return gameStates['still']

def handleStateChange(curState, scEvent):
    # TEMP
    if scEvent=='start':
        return gameStates['play']
