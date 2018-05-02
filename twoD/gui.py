'''
    gui.py : handles the GUI and the visualisation
    of the wavefunction as time passes
'''

import sys
import numpy as np
import pygame
from pygame.locals import (
    QUIT as pgQuit,
    MOUSEBUTTONDOWN as pgMouseDown,
    KEYDOWN as pgKeyDown,
)

from twoD.settings import (
    Nx,
    Ny,
    tileX,
    tileY,
)

from twoD.tools import (
    mod2,
)

def makePalette(pIndex=0):
    import matplotlib.pyplot as plt
    cmap=plt.get_cmap(['magma','GnBu'][pIndex])
    return [
        [int(comp*256) for comp in cmap(((i/255.)))[:3]]
        for i in range(256)
    ]

def initPyGame(pIndex=0):
    pygame.init()
    pygame.display.set_caption('Pyschroedinger 2D. Click to close')
    window=pygame.display.set_mode(
        (
            Nx*tileX,
            Ny*tileY,
        ),
        pygame.DOUBLEBUF,
        8,
    )
    setDrawPalette(pIndex)
    # palette=makePalette()
    # pygame.display.set_palette(palette)
    startnparray=np.zeros((Nx*tileX,Ny*tileY)).astype(int)
    screen = pygame.surfarray.make_surface(startnparray).convert()
    startnparray=np.zeros((Nx,Ny)).astype(int)
    bufferSurf = pygame.surfarray.make_surface(startnparray).convert()
    return {
        'screen': screen,
        'window': window,
        'bufferSurf': bufferSurf,
    }

def setDrawPalette(pIndex=0):
    palette=makePalette(pIndex)
    pygame.display.set_palette(palette)

def integerize(wfunction,maxMod2):
    '''
        makes a complex wavefunction
        into an array of integers 0-255
        rescaling the mod2 according to maxMod2
    '''
    return (0.5+(mod2(wfunction)*254/maxMod2)).astype(int)
    # the slower, bounds-checking form would be:
    # nMat=(0.5+(mod2(wfunction)*254/maxMod2)).astype(int)
    # nMat[nMat>255]=255
    # nMat[nMat<0]=0
    # return nMat

def doPlot(wfunction,replotting=None,title=None,palette=0):
    '''
        all information on the x,y-scale
        is implicit.
        Called once to init the plotting structure
        and subsequently to refresh the plotted data
    '''
    if replotting is None:
        # create everything
        maxMod2=mod2(wfunction).max()
        # setup the plot
        # return handles to refresh the plot
        replotting={
            'maxMod2': maxMod2,
        }
        replotting['pygame']=initPyGame(palette)
        replotting['palette']=palette
        replotting['keyqueue']=[]

    if palette!=replotting['palette']:
        setDrawPalette(palette)
        replotting['palette']=palette

    # refresh the plotting window
    # (including responding to events)
    # 0. cosmetics (title, etc)
    if title is not None:
            pygame.display.set_caption(title)
    # 1. recalculate the integer wf
    # intMod2=integerize(wfunction,replotting['maxMod2'])
    maxMod2=mod2(wfunction).max()
    intMod2=integerize(wfunction,maxMod2)

    # actual on-screen plotting through pygame
    pygame.pixelcopy.array_to_surface(
        replotting['pygame']['bufferSurf'],
        intMod2,
    )
    pygame.transform.scale(
        replotting['pygame']['bufferSurf'],
        (
            Nx*tileX,
            Ny*tileY,
        ),
        replotting['pygame']['screen'],
    )
    replotting['pygame']['window'].blit(
        replotting['pygame']['screen'],
        (0,0),
    )
    pygame.display.flip()
    # 2. respond to events
    for event in pygame.event.get():
        if event.type in {pgQuit, pgMouseDown}:
            pygame.quit()
            sys.exit()
        if event.type in {pgKeyDown} and event.unicode=='q':
            pygame.quit()
            sys.exit()
        if event.type in {pgKeyDown} and event.unicode=='p':
            replotting['keyqueue'].append('p')
    # all done
    return replotting
