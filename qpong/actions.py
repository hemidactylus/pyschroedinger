'''
    actions.py :
        handling of queue of actions to perform
'''

import sys

from qpong.interactive import (
    initialisePlay,
    initialiseMatch,
)

def performActions(mState):
    while(len(mState['actionqueue'])>0):
        ac,mState['actionqueue']=(
            mState['actionqueue'][0],
            mState['actionqueue'][1:],
        )
        #
        acClass,acParam=ac
        if acClass=='music':
            mState['sound']['sounder'].playMusic(acParam)
        elif acClass=='stopmusic':
            mState['sound']['sounder'].stopMusic()
        elif acClass=='sound':
            mState['sound']['sounder'].playSound(acParam)
        elif acClass=='markers':
            markerState={'show': True, 'hide': False}[acParam]
            for scM in mState['scoreMarkers']:
                scM['visible']=markerState
        elif acClass=='pause':
            pauseState={'pause':True,'unpause':False}[acParam]
            for pInfo in mState['playerInfo'].values():
                pInfo['pad']['visible']=not pauseState
            for scM in mState['scoreMarkers']:
                scM['visible']=not pauseState
        elif acClass=='initmatch':
            mState=initialiseMatch(mState)
        elif acClass=='startplay':
            mState=initialisePlay(mState)
        elif acClass=='quitgame':
            sys.exit()
        else:
            raise ValueError('Unknown tuple action "%s"' % ac)
    return mState
