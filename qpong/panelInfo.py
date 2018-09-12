'''
    panelInfo.py :
        module to prepare the information on display
        given the current game state
'''

from utils.units import (
    toTime_fs,
    toMass_MeV_overC2,
)

from qpong.settings import (
    Mu,
)

def calculatePanelInfo(gState,mState):
    pnlInfo=None
    scnInfo=None
    if gState['name']=='paused':
        pnlInfo=[
            '(Field size: %.2E * %.2E fm^2)' % (
                mState['physics']['phLenX'],
                mState['physics']['phLenY'],
            ),
            '(Particle mass: %.2E MeV/c^2)' % (
                toMass_MeV_overC2(Mu),
            ),
            '(Framerate: %.2f frames/sec)' % (
                mState['framerate']
            ),
        ]
        scnInfo=[
            ('Paused',True)
        ]
    elif gState['name']=='still':
        pnlInfo=[
            'Welcome to Quantum Pong.',
        ]
        scnInfo=[
            ('Quantum',True),
            ('Pong',True),
            ('Press "g" to start a game',False),
            ('',False),
            ('Press "i" to quit/interrupt match',False),
            ('Press spacebar to pause match',False),
            ('Arrows and "a/w/s/d" move the pads',False),
            ('',False),
            ('Press "c"/"v" to adjust victory threshold',False),
            ('(currently: %i matches to win)' % mState['matchesToWinPlay'],False),
            ('',False),
            ('Press "1"/"2" to change number of players',False),
            ('(currently: %i players)' % mState['nPlayers'],False),
            ('',False),
            ('Sound is %s' % ['OFF','ON'][int(mState['sound']['active'])],False),
            ('(press "b" to toggle)',False),
            ('',False),
            ('Press "m" for game info/credits',False),
        ]
    elif gState['name']=='play':
        if 'iteration' in mState:
            curMatch=1+len(mState['playScores']['matchScores'])
            if mState['nPlayers']==1:
                scrInfos=[]
            else:
                maxScore=max(mState['playWinner']['scores'].values())
                scrInfos=[
                    '< %s%s | Match %i | %s%s >' % (
                        '*'*mState['playWinner']['scores'][0],
                        ' '*(maxScore-mState['playWinner']['scores'][0]),
                        curMatch,
                        ' '*(maxScore-mState['playWinner']['scores'][1]),
                        '*'*mState['playWinner']['scores'][1],
                    )
                ]
            # additional about-to-score warning
            if mState['nPlayers']>1:
                if max(mState['playWinner']['scores'].values())+1>=mState['matchesToWinPlay']:
                    basePlayMessage='Matchpoint'
                else:
                    basePlayMessage=':)'
                if mState['lastWinningSpree']['winner'] is not None:
                    dangerMessages=[
                        [basePlayMessage,'danger ...','DANGER !']\
                            [mState['lastWinningSpree']['closenessFractionStage']]
                    ]
                else:
                    dangerMessages=[basePlayMessage]
            else:
                dangerMessages=[]
            #
            pnlInfo=scrInfos+[
                'Time elapsed: %.3E femtoseconds' % (
                    toTime_fs(mState['physics']['tau']),
                ),
            ] + dangerMessages
            scnInfo=[]
        else:
            pnlInfo=[
                'About to start ...',
            ]
    elif gState['name']=='quitting':
        pnlInfo=[
            'Quitting game'
        ]
        scnInfo=[
            ('Quit',True),
            ('game?',True),
            ('(y/n)',True),
        ]
    elif gState['name']=='prestarting':
        pnlInfo=[
            'Initializing ...'
        ]
    elif gState['name']=='initplay':
        pnlInfo=[
            'Initializing ...'
        ]
    elif gState['name']=='starting':
        pnlInfo=[
            'Ready?'
        ]
        scnInfo=[
            ('%i' % mState['ctDisplay'],True),
            ('match %i' % (1+len(
                mState['playScores']['matchScores']
            )), False)
        ]
    elif gState['name']=='showendmatch':
        lastWinner=mState['playScores']['matchScores'][-1]
        pnlInfo=[
            'Player %i wins match!' % lastWinner,
        ]
        scnInfo=[
            ('Player %i' % lastWinner,True),
            ('scores!',True),
            ('match %i' % len(
                mState['playScores']['matchScores']
            ),False),
        ]
    elif gState['name']=='showendplay':
        playScores=mState['playWinner']['scores']
        maxScore=max(playScores.values())
        scrInfos=[
            '< %s%s | Final score | %s%s >' % (
                '*'*playScores[0],
                ' '*(maxScore-playScores[0]),
                ' '*(maxScore-playScores[1]),
                '*'*playScores[1],
            )
        ]
        pnlInfo=scrInfos+[
            'Victory for player %i' % mState['playWinner']['winner'],
        ]
        scnInfo=[
            ('Victory!', True),
            ('Player %i' % mState['playWinner']['winner'],True),
        ]
    elif gState['name']=='info':
        pnlInfo=[
            'Game info and credits',
        ]
        scnInfo=[
            ('Game info', True),
            ('Quantum Pong',False),
            ('written by Stefano',False),
            ('www.salamandrina.net',False),
            ('',False),
            ('Credits', True),
            ('Music by:',False),
            ('1,2,3',False),
            ('',False),
            ('Special thanks to:',False),
            ('a,b,c',False),
            ('',False),
            ('(press "i" to go back)',False),
        ]
    else:
        raise NotImplementedError

    return pnlInfo,scnInfo
