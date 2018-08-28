'''
    sound.py :
        driver for music and sound effects
'''

import pygame
import os

musicDirs={
    'game': 'music/menu',
    'menu': 'music/game',
}

def listMp3Files(dir):
    return [
        os.path.join(dir,fname)
        for fname in os.listdir(dir)
        if fname[-4:].lower()=='.mp3'
    ]

def pickRandom(lst):
    print('HERE RANDOMIZE AND REMEMBER STATUS TO AVOID REPEATING')
    # and if list empty return none and so on
    # and then reorganize the sound effects in a different way
    return lst[0]

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
            k: listMp3Files(os.path.join(self.resourcePath,v))
            for k,v in musicDirs.items()
        }
        #
        print(self.musicFilesMap)
        #
        self.sounds={
            sname: pygame.mixer.Sound(os.path.join(
                self.resourcePath,
                fname,
            ))
            for sname,fname in zip(
                ['h','l','b'],
                ['high.wav','low.wav','beep.wav'],
            )
        }

    def playSound(self,sName):
        self.sounds[sName].play()

    def playMusic(self,mode):
        qFilename=pickRandom(self.musicFilesMap[mode])
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
