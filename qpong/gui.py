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

from qpong.settings import (
    Nx,
    Ny,
)

from qpong.interactiveSettings import (
    tileX,
    tileY,
    panelBackgroundColor,
    panelForegroundColor,
    screenForegroundColor,
    labelFontSize,
    titleFontSize,
    potentialColor,
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
    pygame.display.set_caption('')
    pygame.mouse.set_visible(False)
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
        labelFont=pygame.font.SysFont("Courier New", labelFontSize, bold=True)
        titleFont=pygame.font.SysFont("Courier New", titleFontSize, bold=True)
    else:
        topPanel=None
        npTopPanel=None
        labelFont=None
        titleFont=None
    return {
        'screen': screen,
        'window': window,
        'bufferSurf': bufferSurf,
        'topPanel': topPanel,
        'npTopPanel': npTopPanel,
        'labelFont': labelFont,
        'titleFont': titleFont,
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

def rectanglePlacement(sizeList,panelAreaSize):
    '''
        given a list of rectangle sizes (e.g. message blocks)
        and the size of a containing area,
        prepares a list of offsets for each block's
        top-left corner to achieve centering
    '''
    totalHeight=sum(s[1] for s in sizeList)
    hLinePos=int(0.5*(panelAreaSize[1]-totalHeight))
    positions=[]
    #
    for ind,l in enumerate(sizeList):
        wLinePos=int(0.5*(panelAreaSize[0]-sizeList[ind][0]))
        positions.append((wLinePos,hLinePos))
        hLinePos+=sizeList[ind][1]
    return positions

def doPlot(
        wfunction,
        replotting=None,
        artifacts=[],
        keysToCatch=set(),
        keysToSend=set(),
        specialColors=[potentialColor],
        panelHeight=0,
        panelInfo=None,
        screenInfo=None,
    ):
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

    # in-panel written text
    if panelInfo is not None:
        pygame.pixelcopy.array_to_surface(
            replotting['pygame']['topPanel'],
            replotting['pygame']['npTopPanel'],
        )
        # creation of the rendered labels
        panelLabelList=[
            replotting['pygame']['labelFont'].render(panelLine,False,panelForegroundColor,0)
            for ind,panelLine in enumerate(panelInfo)
        ]
        panelsizes=[lbl.get_size() for lbl in panelLabelList]
        panelAreaSize=(Nx*tileX,replotting['panelHeight'])
        panelPositions=rectanglePlacement(panelsizes,panelAreaSize)

        for l,sz in zip(panelLabelList,panelPositions):
            replotting['pygame']['topPanel'].blit(
                l,
                sz,
            )
        # finally, draw the completed top panel on the window
        replotting['pygame']['window'].blit(
            replotting['pygame']['topPanel'],
            (0,0),
        )

    # on-screen written text
    if screenInfo is not None:
        screenLabelList=[
            (
                replotting['pygame']['titleFont'] if largeLine else replotting['pygame']['labelFont']
            ).render(panelLine,False,screenForegroundColor,0)
            for panelLine,largeLine in screenInfo
        ]
        # centering and positioning
        screenSizes=[lbl.get_size() for lbl in screenLabelList]
        screenAreaSize=(Nx*tileX,Ny*tileY)
        screenPositions=rectanglePlacement(screenSizes,screenAreaSize)
        for l,sz in zip(screenLabelList,screenPositions):
            replotting['pygame']['window'].blit(
                l,
                (sz[0],replotting['panelHeight']+sz[1]),
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
