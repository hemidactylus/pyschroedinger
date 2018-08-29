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
}

class Sounder():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.resourcePath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'resources'
        )
        #
        self.musicFilesMap={
            k: {
                fname: fname
                for fname in self.listMp3Files(os.path.join(self.resourcePath,v))
            }
            for k,v in musicDirs.items()
        }
        self.lastMusicPicked={
            k: None
            for k in musicDirs.keys()
        }
        #
        self.soundMap={
            k: {
                fname: pygame.mixer.Sound(fname)
                for fname in self.listWavFiles(os.path.join(self.resourcePath,v))
            }
            for k,v in soundDirs.items()
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

    def getSomeMusic(self,mode):
        '''
            if no songs, return None
            if one, return it
            if many, exclude the most recently
                played and pick at random
        '''
        if len(self.musicFilesMap[mode])==0:
            mChosen=None
        elif len(self.musicFilesMap[mode])==1:
            mChosen=self.musicFilesMap[mode][0]
        else:
            mPool=[
                (mKey,mFile)
                for mKey,mFile in self.musicFilesMap[mode].items()
                if mKey!=self.lastMusicPicked[mode]
            ]
            nInPool=len(mPool)
            mChosen=mPool[random.randint(0,nInPool-1)]
        self.lastMusicPicked[mode]=mChosen[0]
        return mChosen[1]

    def playSound(self,sName):
        print('THIS MUST BE A GENERALISATION OF THE PICKER ABOVE')
        qSound=list(self.soundMap[sName].items())[0][1]
        qSound.play()

    def playMusic(self,mode):
        qFilename=self.getSomeMusic(mode)
        if qFilename is not None:
            pygame.mixer.music.load(qFilename)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

    def stopMusic(self):
        if self.musicPlaying():
            pygame.mixer.music.stop()

    def musicPlaying(self):
        return pygame.mixer.music.get_busy()

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
