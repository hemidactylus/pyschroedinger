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
    arrowKeyMap,
    potentialColor,
)

from twoD.tools import (
    mod2,
)

def makePalette(pIndex=0):
    '''
        we leave a last single color for non-wavefunction
        display (in particular for the potential).
        Not a big waste even in case we are not interactive
    '''
    import matplotlib.pyplot as plt
    cmap=plt.get_cmap(['magma','GnBu'][pIndex])
    return [
        [int(comp*256) for comp in cmap(((i/254.)))[:3]]
        for i in range(255)
    ]+[potentialColor]

def initPyGame(pIndex=0,saveImage=False):
    pygame.init()
    pygame.display.set_caption('Pyschroedinger 2D. Click to close')
    window=pygame.display.set_mode(
        (
            Nx*tileX,
            Ny*tileY,
        ),
        pygame.DOUBLEBUF,
        8 if not saveImage else 24,
    )
    if not saveImage:
        setDrawPalette(pIndex)
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
    # to enhance the low values' coloring:
    # return (0.5+((mod2(wfunction)/maxMod2)**0.43)*254).astype(int)
    # the standard coloring:
    if maxMod2>0:
        return (0.5+(mod2(wfunction)*253/maxMod2)).astype(int)
    else:
        return mod2(wfunction).astype(int)
    # the slower, bounds-checking form of the latter would be:
    # nMat=(0.5+(mod2(wfunction)*254/maxMod2)).astype(int)
    # nMat[nMat>255]=255
    # nMat[nMat<0]=0
    # return nMat

# Threshold of value (in units of 256) above which we draw the potential
# instead of the wavefunction (for saveImage only)
DRAW_POTENTIAL_THRESHOLD=80
def mapToPalette(colArray,nparray,potarray,refPalette,refPotPalette):
    for x in range(nparray.shape[0]):
        for y in range(nparray.shape[1]):
            colArray[x][y]=np.array(refPalette[nparray[x][y]])
            if potarray[x][y]>DRAW_POTENTIAL_THRESHOLD:
                colArray[x][y]=np.array(refPotPalette[potarray[x][y]])

def doPlot(wfunction,replotting=None,title=None,palette=0,photoIndex=None,saveImage=False,potential=None,artifacts=[]):
    '''
        all information on the x,y-scale
        is implicit.
        Called once to init the plotting structure
        and subsequently to refresh the plotted data

        To save frames for generating animated GIFs:
            - in the init call, pass potential and saveImage=True
            - for subsequent calls, to create a frame image,
              pass the integer photoIndex
            
            # Careful: with saveImage we do not use any palette and
              employ 24-bit colors natively (slowew)
    '''
    if replotting is None:
        # create everything
        maxMod2=mod2(wfunction).max()
        # setup the plot
        # return handles to refresh the plot
        replotting={
            'maxMod2': maxMod2,
        }
        replotting['pygame']=initPyGame(palette,saveImage)
        replotting['keyqueue']=[]
        replotting['saveImage']=saveImage
        replotting['palette']=palette
        if replotting['saveImage']:
            replotting['usedPalette']=makePalette(palette)
            maxPot=mod2(potential.astype(complex)).max()
            replotting['potential']=integerize(potential.astype(complex),maxPot)
            replotting['potPalette']=makePalette(1)

    if replotting['saveImage']:
        if palette!=replotting['palette']:
            replotting['usedPalette']=makePalette(palette)
            replotting['palette']=palette
    else:
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

    # actual on-screen plotting through pygame (and optionally saving)
    if replotting['saveImage']:
        # non-optimised saving of the current frame
        colArray=np.zeros((Nx,Ny,3)).astype(int)
        pygame.pixelcopy.surface_to_array(colArray,replotting['pygame']['bufferSurf'])
        mapToPalette(colArray,intMod2,replotting['potential'],replotting['usedPalette'],replotting['potPalette'])
        pygame.pixelcopy.array_to_surface(replotting['pygame']['bufferSurf'],colArray)
    else:
        if potential is not None:
            potThreshold=0.5*potential.max()
            intMod2[potential>=potThreshold]=255
        pygame.pixelcopy.array_to_surface(
            replotting['pygame']['bufferSurf'],
            intMod2.reshape((Nx,Ny)),
        )
    # artifacts
    for art,pos in artifacts:
        # print(dir(replotting['pygame']['bufferSurf']))
        replotting['pygame']['bufferSurf'].blit(art,pos)
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
        (0,0),
    )
    pygame.display.flip()
    #
    if photoIndex is not None:
        print('Saving frame %i' % photoIndex)
        pygame.image.save(replotting['pygame']['screen'].convert(24),'frame%06i.bmp' % photoIndex)
    #
    # 2. respond to events
    for event in pygame.event.get():
        if event.type in {pgQuit, pgMouseDown}:
            replotting['keyqueue'].append('q')
        if event.type in {pgKeyDown} and event.unicode=='q':
            replotting['keyqueue'].append('q')
        if event.type in {pgKeyDown} and event.unicode=='p':
            replotting['keyqueue'].append('p')
        if event.type in {pgKeyDown} and event.unicode=='s':
            replotting['keyqueue'].append('s')
        # if event.type in {pgKeyDown} and event.key in arrowKeyMap:
        #     replotting['keyqueue'].append(event.key)
    kpresses= pygame.key.get_pressed()
    for kDir in arrowKeyMap:
        if kpresses[kDir]:
            replotting['keyqueue'].append(kDir)
    return replotting
