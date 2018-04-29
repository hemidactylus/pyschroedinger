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

def makePalette():
    # FIXME
    return [
        [int(i*255./256.+0.5)]*3
        for i in range(256)
    ]

def initPyGame():
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
    palette=makePalette()
    pygame.display.set_palette(palette)
    startnparray=np.zeros((Nx*tileX,Ny*tileY)).astype(int)
    screen = pygame.surfarray.make_surface(startnparray).convert()
    startnparray=np.zeros((Nx,Ny)).astype(int)
    bufferSurf = pygame.surfarray.make_surface(startnparray).convert()
    return {
        'screen': screen,
        'window': window,
        'bufferSurf': bufferSurf,
    }

def integerize(wfunction,maxMod2):
    '''
        makes a complex wavefunction
        into an array of integers 0-255
        rescaling the mod2 according to maxMod2
    '''
    return (0.5+(mod2(wfunction)*255/maxMod2)).astype(int)

def doPlot(wfunction,replotting=None,title=None):
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
        replotting['pygame']=initPyGame()

    # refresh the plotting window
    # (including responding to events)
    # 0. cosmetics (title, etc)
    if title is not None:
            pygame.display.set_caption(title)
    # 1. recalculate the integer wf
    intMod2=integerize(wfunction,replotting['maxMod2'])

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
    # all done
    return replotting
