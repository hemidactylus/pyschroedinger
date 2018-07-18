'''
    stateMachine.py : this handles the abstract
    game state machine and its transitions.
'''

gameStates={
    'still': {
        'integrate': False,
    },
    'play': {
        'integrate': True,
    },
}

def initState():
    return 'still'

def handleStateChange(curState, scEvent):
    pass
