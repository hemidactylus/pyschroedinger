'''
    artifacts.py : handling of "sprites" (i.e. artifacts)
    as colorkey-Surfaces + positioning, to be passed to the plotting
    gui module

    An artifact is a dict
        {
            'pos': (x,y), # of upper-left pixel
            'surface': a colorkey surface
        }
'''

import pygame.surface

def makeFilledBlockArtifact(pPos,pSize,color):
    art=pygame.surface.Surface(
        pSize,
        0,
        8,
    )
    art.fill(color)
    return {
        'pos': pPos,
        'surface': art,
        'offset': (0,0),
    }

def makeCheckerboardRectangularArtifact(Nx,Ny,posX,posY,widthX,heightY,color,transparentKey):
    '''
        once the area is constructed, the pixels are
        filled in a checkerboard fashion.
    '''
    pPosX=int(Nx*posX)
    pPosY=int(Ny*posY)
    pPos=(pPosX,pPosY)
    pLength=int(Nx*widthX)
    pHeight=int(Ny*heightY)
    art=pygame.surface.Surface(
        (pLength,pHeight),
        0,
        8,
    )
    art.fill(transparentKey)
    for x in range(pLength):
        for y in range(pHeight):
            if (x+y)%2==0:
                art.set_at((x,y),color)
    art.set_colorkey(transparentKey)
    return {
        'pos': pPos,
        'surface': art,
        'offset': (0,0),
    }

def makeRectangularArtifactList(Nx,Ny,posX,posY,color,transparentKey):
    '''
        returns an artifact of a rectangular frame.
            pos* < 0.5, width* are in 0-1 units
        color is a number e.g. 255
        transparentKey = 0 usually
    '''
    pPosX=int(Nx*posX)
    pPosY=int(Ny*posY)
    pLength=Nx-2*pPosX
    pHeight=Ny-2*pPosY
    return [
        makeFilledBlockArtifact(
            (pPosX,pPosY),
            (pLength,1),
            color,
        ),
        makeFilledBlockArtifact(
            (pPosX,pPosY+pHeight-1),
            (pLength,1),
            color,
        ),
        makeFilledBlockArtifact(
            (pPosX,pPosY),
            (1,pHeight),
            color,
        ),
        makeFilledBlockArtifact(
            (pPosX+pLength-1,pPosY),
            (1,pHeight),
            color,
        ),
    ]

def makeCircleArtifact(Nx,Ny,centerX,centerY,radiusX,radiusY,color,transparentKey):
    pRadiusX=int(Nx*radiusX)
    pRadiusY=int(Ny*radiusY)
    cWidth=int(2*pRadiusX+1)
    cHeight=int(2*pRadiusY+1)
    pCenterX=int(centerX*Nx)
    pCenterY=int(centerY*Ny)
    circle=pygame.surface.Surface(
        (cWidth,cHeight),
        0,
        8,
    )
    circle.fill(transparentKey)
    for px in range(cWidth):
        for py in range(cHeight):
            r=(
                ((px-pRadiusX)/pRadiusX)**2 + \
                ((py-pRadiusY)/pRadiusY)**2
            )**0.5
            if r<=1.1 and r>0.95:
                circle.set_at((px,py),color)
    circle.set_colorkey(transparentKey)
    return {
        'pos': (pCenterX,pCenterY),
        'surface': circle,
        'offset': (-pRadiusX,-pRadiusY)
    }
