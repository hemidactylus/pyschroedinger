'''
    interactive.py :
      tools for qpong
'''
from itertools import count
import time
import sys

from twoD.settings import (
    Nx,
    Ny,
    deltaLambdaX,
    deltaLambdaY,
)
from qpong.interactiveSettings import (
    fieldBevelX,
    fieldBevelY,
    potPlayerPadHeight,
    winningFraction,
    potBorderWallHeight,
    patchRadii,
)

from twoD.wfunctions import (
    wavePacket,
)
from twoD.potentials import (
    ellipticHolePotential,
    rectangularHolePotential,
)

from twoD.artifacts import (
    makeRectangularArtifactList,
    makeCircleArtifact,
    makeCheckerboardRectangularArtifact,
    makeFilledBlockArtifact,
)

from twoD.tools import (
    combineWFunctions,
    combinePotentials,
)

def initPhi():
    # here the initial wave packed is created
    # STILL TO MAKE WELL CONFIGURABLE
    phi=combineWFunctions(
        [
            wavePacket(Nx,Ny,c=(0.25,0.25),ph0=(+10,+5),sigma2=(0.002,0.002),weight=1),
            wavePacket(Nx,Ny,c=(0.75,0.75),ph0=(-10,-5),sigma2=(0.002,0.002),weight=1),
        ],
        deltaLambdaXY=deltaLambdaX*deltaLambdaY,
    )
    return phi

def initPot(patchPosList,prevPot):
    '''
        given a one-off background potential
        and a list of positions for the 'patches'
        (the player pads), the potential is computed
    '''
    patchPotList=[
        ellipticHolePotential(
            Nx,
            Ny,
            pPos=patchPos,
            pRadius=(0.1,0.1),
            pThickness=0.01,
            vIn=potPlayerPadHeight,
            vOut=0,
        )
        for patchPos in patchPosList
    ]
    return combinePotentials(
        [
            prevPot,
        ]+patchPotList, 
    ), patchPotList

def prepareBasePotential():
    return rectangularHolePotential(
        Nx,
        Ny,
        pPos=(0.0,0.0,1.,1.),
        pThickness=(0.0001,0.0001),
        vIn=0,
        vOut=potBorderWallHeight,
    )

def fixCursorPosition(pp,ps,rdii,bbox):
    '''
        ensures a player-cursor position
        falls within the allowed region:
            pp = previous position
            ps = increments
            rdii = radius in the xy dirs
            bbox = boundary regions
    '''
    nPos=[pp[0]+ps[0],pp[1]+ps[1]]
    if nPos[0]-rdii[0]<bbox[0]:
        nPos[0]=bbox[0]+rdii[0]
    if nPos[0]+rdii[0]>bbox[2]:
        nPos[0]=bbox[2]-rdii[0]
    if nPos[1]-rdii[1]<bbox[1]:
        nPos[1]=bbox[1]+rdii[1]
    if nPos[1]+rdii[1]>bbox[3]:
        nPos[1]=bbox[3]-rdii[1]
    return tuple(nPos)

def preparePlayerInfo(nPlayers):
    '''
        returns a description of the geometric
        features of the player(s).

        Also prepares the patch artifacts for the players
    '''
    if nPlayers==1:
        playerInfo={
            0: {
                'bbox': [
                    fieldBevelX,
                    fieldBevelY,
                    1-fieldBevelX,
                    1-fieldBevelY,
                ],
                'patchInitPos': (0.5,0.5),
            },
        }
    elif nPlayers==2:
        playerInfo={
            0: {
                'bbox': [
                    0.5+0.5*fieldBevelX,
                    fieldBevelY,
                    1-fieldBevelX,
                    1-fieldBevelY,
                ],
                'patchInitPos': (0.75,0.5),
            },
            1: {
                'bbox': [
                    fieldBevelX,
                    fieldBevelY,
                    0.5-0.5*fieldBevelX,
                    1-fieldBevelY,
                ],
                'patchInitPos': (0.25,0.5),
            },
        }
    else:
        raise ValueError('nPlayers cannot be %i' % nPlayers)
    ###
    for plIndex,plInfo in playerInfo.items():
        plInfo['pad']=makeCircleArtifact(
            Nx=Nx,
            Ny=Ny,
            centerX=0.5,
            centerY=0.5,
            radiusX=patchRadii[0],
            radiusY=patchRadii[1],
            color=254-plIndex,
            transparentKey=0,
        )
        plInfo['patchPos']=plInfo['patchInitPos']
    return playerInfo

def scorePosition(normMap):
    '''
        given a map from each (vertical)
        sector index to the fraction of psi2
        residing in that sector,
        computes a score (0 to 1)
        telling how close to winning the players
        are.
    '''
    renorm={
        0: max(0,1-normMap[0]/winningFraction),
        1: max(0,1-normMap[3]/winningFraction),
    }
    if renorm[0]<renorm[1]:
        s=-1+renorm[0]/renorm[1]
    elif renorm[0]>renorm[1]:
        s=+1-renorm[1]/renorm[0]
    else:
        s=0.0
    return 0.5*(1+s)
