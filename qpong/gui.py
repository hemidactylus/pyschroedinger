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
    potentialColor,
)

from qpong.interactiveSettings import (
    panelBackgroundColor,
    panelForegroundColor,
    screenForegroundColor,
)

from twoD.tools import (
    mod2,
)

def makePalette(specialColors=[]):
    '''
        we leave a last single color for non-wavefunction
        display (in particular for the potential).
        Not a big waste even in case we are not interactive
    '''
    nSpecials=len(specialColors)
    import matplotlib.pyplot as plt
    cmap=plt.get_cmap('magma')
    return [
        [int(comp*256) for comp in cmap(((i/(255.0-nSpecials))))[:3]]
        for i in range(256-nSpecials)
    ]+specialColors

def initPyGame(specialColors=[],panelHeight=0):
    pygame.init()
    pygame.display.set_caption('Pyschroedinger 2D. Click to close')
    window=pygame.display.set_mode(
        (
            Nx*tileX,
            Ny*tileY+panelHeight,
        ),
        pygame.DOUBLEBUF | pygame.NOFRAME,
        8,
    )
    setDrawPalette(specialColors=specialColors)
    startnparray=np.zeros((Nx*tileX,Ny*tileY)).astype(int)
    screen = pygame.surfarray.make_surface(startnparray).convert()
    startnparray=np.zeros((Nx,Ny)).astype(int)
    bufferSurf = pygame.surfarray.make_surface(startnparray).convert()
    if panelHeight>0:
        startArrayTopPanel=np.zeros((Nx*tileX,panelHeight)).astype(int)
        topPanel=pygame.surfarray.make_surface(startArrayTopPanel).convert()
        npTopPanel=np.zeros((Nx*tileX,panelHeight),dtype=int)
        npTopPanel[:][:]=panelBackgroundColor
        labelFont=pygame.font.SysFont("Courier New", 20, bold=True)
    else:
        topPanel=None
        npTopPanel=None
        labelFont=None
    return {
        'screen': screen,
        'window': window,
        'bufferSurf': bufferSurf,
        'topPanel': topPanel,
        'npTopPanel': npTopPanel,
        'labelFont': labelFont,
    }

def setDrawPalette(specialColors=[]):
    palette=makePalette(specialColors=specialColors)
    pygame.display.set_palette(palette)

def integerize(wfunction,maxMod2,paletteRange):
    '''
        makes a complex wavefunction
        into an array of integers 0-255
        rescaling the mod2 according to maxMod2
        paletteRange=256-nSpecialColors
    '''
    # to enhance the low values' coloring:
    # return (0.5+((mod2(wfunction)/maxMod2)**0.43)*254).astype(int)
    # the standard coloring:
    if maxMod2>0:
        return (0.5+(mod2(wfunction)*(paletteRange-2)/maxMod2)).astype(int)
    else:
        return mod2(wfunction).astype(int)
    # the slower, bounds-checking form of the latter would be:
    # nMat=(0.5+(mod2(wfunction)*254/maxMod2)).astype(int)
    # nMat[nMat>255]=255
    # nMat[nMat<0]=0
    # return nMat

def doPlot(wfunction,replotting=None,artifacts=[],keysToCatch=set(),keysToSend=set(),specialColors=[potentialColor],panelHeight=0,panelInfo=None):
    '''
        all information on the x,y-scale
        is implicit.
        Called once to init the plotting structure
        and subsequently to refresh the plotted data
    '''
    if replotting is None:
        # create everything
        maxMod2=mod2(wfunction).max() if wfunction is not None else 0.0
        # setup the plot
        # return handles to refresh the plot
        replotting={
            # FIXME is this still used? (NO!)
            'maxMod2': maxMod2,
        }
        replotting['pygame']=initPyGame(specialColors,panelHeight=panelHeight)
        replotting['panelHeight']=panelHeight
        replotting['keyqueue']=[]
        replotting['paletteRange']=256-len(specialColors)
        replotting['specialColors']=specialColors

    # refresh the plotting window
    # (including responding to events)
    # 1. recalculate the integer wf
    if wfunction is not None:
        maxMod2=mod2(wfunction).max()
        intMod2=integerize(wfunction,maxMod2,paletteRange=replotting['paletteRange'])

    if wfunction is not None:
        pygame.pixelcopy.array_to_surface(
            replotting['pygame']['bufferSurf'],
            intMod2.reshape((Nx,Ny)),
        )
    else:
        pygame.pixelcopy.array_to_surface(
            replotting['pygame']['bufferSurf'],
            np.zeros((Nx,Ny),dtype=int),
        )
    # artifacts
    for art in artifacts:
        if art['visible']:
            replotting['pygame']['bufferSurf'].blit(
                art['surface'],
                tuple(p+o for p,o in zip(art['pos'],art['offset'])),
            )
    #
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
        (0,replotting['panelHeight']),
    )
    #
    if panelInfo is not None:
        pygame.pixelcopy.array_to_surface(
            replotting['pygame']['topPanel'],
            replotting['pygame']['npTopPanel'],
        )
        # creation of the rendered labels
        labelList=[
            replotting['pygame']['labelFont'].render(panelLine,False,panelForegroundColor,0)
            for ind,panelLine in enumerate(panelInfo)
        ]
        for ind,l in enumerate(labelList):
            l.convert(8)
            l.set_colorkey(0)
            replotting['pygame']['topPanel'].blit(l,(5,5+20*ind))
        # finally, draw the completed top panel on the window
        replotting['pygame']['window'].blit(
            replotting['pygame']['topPanel'],
            (0,0),
        )
        # TEST to write below
        onScreenLabelList=[
            replotting['pygame']['labelFont'].render(panelLine,False,screenForegroundColor,0)
            for ind,panelLine in enumerate(panelInfo)
        ]
        for ind,l in enumerate(onScreenLabelList):
            replotting['pygame']['window'].blit(
                l,
                (15,replotting['panelHeight']+10+20*ind),
            )

    pygame.display.flip()

    # 2. respond to events
    for event in pygame.event.get():
        if event.type==pgKeyDown and event.unicode in keysToSend:
            replotting['keyqueue'].append(event.unicode)
    kpresses=pygame.key.get_pressed()
    for kDir in keysToCatch:
        if kpresses[kDir]:
            replotting['keyqueue'].append(kDir)
    return replotting
