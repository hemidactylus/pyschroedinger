'''
    sound.py :
        driver for music and sound effects
'''

import pygame
import os
import random

# directory settings
musicDirs={
    'game': 'music/game',
    'menu': 'music/menu',
}
soundDirs={
    'danger': 'sound/danger',
    'victory': 'sound/victory',
    'matchscore': 'sound/matchscore',
    'quit': 'sound/quit',
    'skewing_balance': 'sound/skewing_balance',
    'restoring_balance': 'sound/restoring_balance',
    'ct_1': 'sound/ct_1',
    'ct_2': 'sound/ct_2',
    'ct_3': 'sound/ct_3',
    'nplayers': 'sound/nplayers',
    'n_matches_up': 'sound/n_matches_up',
    'n_matches_down': 'sound/n_matches_down',
    'sound_on': 'sound/sound_on',
}

class Sounder():
    def __init__(self,active):
        pygame.init()
        pygame.mixer.init()
        self.active=active
        self.nominalMusicMode=None
        self.resourcePath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'resources'
        )
        #
        self.soundResources={
            'music': {
                k: {
                    'map': {
                        fname: fname
                        for fname in self.listMp3Files(os.path.join(self.resourcePath,v))
                    },
                    'lastPlayed': None,
                }
                for k,v in musicDirs.items()
            },
            'sound': {
                k: {
                    'map': {
                        fname: pygame.mixer.Sound(fname)
                        for fname in self.listWavFiles(os.path.join(self.resourcePath,v))
                    },
                    'lastPlayed': None,
                }
                for k,v in soundDirs.items()
            },
        }

    @staticmethod
    def listFilesByExt(dir,ext):
        try:
            return [
                os.path.join(dir,fname)
                for fname in os.listdir(dir)
                if fname[-len(ext):].lower()==ext
            ]
        except:
            print('** Cannot get <%s> files in %s' % (ext,dir))
            return []

    @staticmethod
    def listMp3Files(dir):
        return Sounder.listFilesByExt(dir,'.mp3')

    @staticmethod
    def listWavFiles(dir):
        return Sounder.listFilesByExt(dir,'.wav')

    def getAResource(self,kind,mode):
        '''
            kind=sound, music
            mode=the subtype (e.g. for music: 'menu')

            if no items, return None
            if one, returns it
            if many, excludes the most recently
                played and picks at random
                (saving the choice for next time)
        '''
        if len(self.soundResources[kind][mode]['map'])==0:
            mKey,mChosen=None,None
        elif len(self.soundResources[kind][mode]['map'])==1:
            mKey,mChosen=list(self.soundResources[kind][mode]['map'].items())[0]
        else:
            mPool=[
                (mKey,mFile)
                for mKey,mFile in self.soundResources[kind][mode]['map'].items()
                if mKey!=self.soundResources[kind][mode]['lastPlayed']
            ]
            nInPool=len(mPool)
            mKey,mChosen=mPool[random.randint(0,nInPool-1)]
        self.soundResources[kind][mode]['lastPlayed']=mKey
        return mChosen

    def getAMusic(self,mode):
        return self.getAResource('music',mode)

    def getASound(self,mode):
        return self.getAResource('sound',mode)

    def playSound(self,sName):
        if self.active:
            qSound=self.getASound(sName)
            if qSound is not None:
                qSound.play()

    def playMusic(self,mode):
        self.nominalMusicMode=mode
        if self.active:
            qFilename=self.getAMusic(mode)
            if qFilename is not None:
                pygame.mixer.music.load(qFilename)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)

    def stopMusic(self):
        self.nominalMusicMode=None
        if self.musicPlaying():
            pygame.mixer.music.stop()

    def musicPlaying(self):
        return pygame.mixer.music.get_busy()

    def setActive(self,active):
        self.active=active
        if not self.active:
            if self.musicPlaying():
                pygame.mixer.music.stop()
        else:
            if self.nominalMusicMode is not None:
                self.playMusic(self.nominalMusicMode)

if __name__=='__main__':

    doMusic=True
    doSounds=True

    snd=Sounder()

    #
    import time
    import sys
    if doMusic:
        snd.playMusic(3)
        print('p')

    for i in range(40):
        print('%i (%s) ' % (i,snd.musicPlaying()))
        if i==12:
            snd.playSound('h')
        if i==16 or i==18:
            snd.playSound('l')
        if i==17:
            snd.playSound('h')
        sys.stdout.flush()
        time.sleep(.25)

    if doMusic:
        print('\ns')
        snd.stopMusic()
