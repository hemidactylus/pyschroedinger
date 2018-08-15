'''
    interactive.py :
      tools for qpong
'''
import numpy as np

from twoD.settings import (
    Nx,
    Ny,
    Mu,
    deltaTau,
    deltaLambdaX,
    deltaLambdaY,
    periodicBCX,
    periodicBCY,
    drawFreq,
    LambdaX,
    LambdaY,
)
from qpong.interactiveSettings import (
    fullArrowKeyMap,
    fieldBevelX,
    fieldBevelY,
    potPlayerPadHeight,
    winningFraction,
    potBorderWallHeight,
    patchRadii,
    patchThickness,
    potWavefunctionDampingDivider,
)

from twoD.wfunctions import (
    wavePacket,
)
from twoD.potentials import (
    ellipticHolePotential,
    rectangularHolePotential,
)

from twoD.dynamics import (
    VariablePotSparseRK4Integrator,
)

from qpong.artifacts import (
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
            wavePacket(Nx,Ny,c=(0.25,0.25),ph0=(  0,+20),sigma2=(0.006,0.006),weight=1),
            wavePacket(Nx,Ny,c=(0.75,0.75),ph0=(  0,-20),sigma2=(0.006,0.006),weight=1),
            wavePacket(Nx,Ny,c=(0.75,0.25),ph0=(-20,  0),sigma2=(0.006,0.006),weight=1),
            wavePacket(Nx,Ny,c=(0.25,0.75),ph0=(+20,  0),sigma2=(0.006,0.006),weight=1),
        ],
        deltaLambdaXY=deltaLambdaX*deltaLambdaY,
    )
    return phi

def initPatchPotential():
    '''
        prepares a single patch potential
        centred in a 2*Nx,2*Ny plane
        acting as a cache at each patch
        repositioning
    '''
    pPot=ellipticHolePotential(
        2*Nx,
        2*Ny,
        pPos=(0.5,0.5),
        pRadius=tuple(0.5*r for r in patchRadii),
        pThickness=0.5*patchThickness,
        vIn=potPlayerPadHeight,
        vOut=0,
        reshape=False,
    )
    return {
        'pot': pPot,
        'centre': (Nx,Ny),
        'halfSize': (Nx,Ny),
    }

def assemblePotentials(patchPosList,patchPot,backgroundPot,matrixRepo=None):
    '''
        given a one-off background potential,
        a cached patch potential
        (as returned by initPatchPotential)
        and a list of positions for the 'patches'
        (the player pads), the potential is computed
    '''
    if matrixRepo is not None:
        varPot=matrixRepo['varPot']
        varPot[:][:]=0.0
    else:
        varPot=np.zeros((Nx,Ny),dtype=float)
    pcX,pcY=patchPot['centre']
    for patchPos in patchPosList:
        pPosIntX,pPosIntY=(int(patchPos[0]*Nx),int(patchPos[1]*Ny))
        for vpX in range(Nx):
            for vpY in range(Ny):
                varPot[vpX][vpY]+=patchPot['pot'][(vpX-pPosIntX)+pcX][(vpY-pPosIntY)+pcY]
    rVarPot=varPot.reshape((Nx*Ny))
    fPot=combinePotentials(
        [
            backgroundPot,
            rVarPot
        ],
        matrixRepo=matrixRepo,
    )
    # a linear approximation is not particularly faster than this (see below)
    if matrixRepo is not None:
        dampingFactor=matrixRepo['dampingFactor']
        # in-place linear approx
        # maxP,minP=np.max(fPot),np.min(fPot)
        # dampingFactor-=minP
        # dampingFactor/=(maxP-minP)
        # dampingFactor**=16
        # dampingFactor-=1
        # in-place exp damping
        np.exp(-fPot/potWavefunctionDampingDivider,dampingFactor)
    else:
        dampingFactor=np.exp(-fPot/potWavefunctionDampingDivider)
    return fPot,dampingFactor

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
        plInfo['pad']['pos']=(
            int((plInfo['patchPos'][0])*Nx),
            int((plInfo['patchPos'][1])*Nx),
        )
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

def prepareMatrixRepository():
    varPot=np.zeros((Nx,Ny),dtype=float)
    dampingFactor=varPot.reshape((Nx*Ny))
    fullPotential=np.zeros(Nx*Ny,dtype=float)
    return {
        'varPot': varPot,
        'dampingFactor': dampingFactor,
        'fullPotential': fullPotential,
    }

def initialisePlay(mutableGameState):
    '''
        this is called when the "play" starts,
        i.e. the full set of N matches
    '''
    mutableGameState['playScores']={
        'matchScores': [],
    }
    return mutableGameState

def initialiseMatch(mutableGameState):
    '''
        this initialises the single match, the
        one that has a single outcome
        (a player scores 1 point and that's it)
    '''

    mutableGameState['iteration']=0
    mutableGameState['playerInfo']=preparePlayerInfo(mutableGameState['nPlayers'])
    mutableGameState['arrowKeyMap']={
        k: v
        for k,v in fullArrowKeyMap.items()
        if v['player'] in mutableGameState['playerInfo']
    }
    (
        mutableGameState['physics']['pot'],
        mutableGameState['physics']['damping'],
    )=assemblePotentials(
        patchPosList=[
            plInfo['patchInitPos']
            for plInfo in mutableGameState['playerInfo'].values()
        ],
        patchPot=mutableGameState['patchPot'],
        backgroundPot=mutableGameState['basePot'],
        matrixRepo=mutableGameState['globalMatrixRepo'],
    )
    mutableGameState['physics']['integrator']=VariablePotSparseRK4Integrator(
        wfSizeX=Nx,
        wfSizeY=Ny,
        deltaTau=deltaTau,
        deltaLambdaX=deltaLambdaX,
        deltaLambdaY=deltaLambdaY,
        nIntegrationSteps=drawFreq,
        vPotential=mutableGameState['physics']['pot'],
        periodicBCX=periodicBCX,
        periodicBCY=periodicBCY,
        mu=Mu,
        exactEnergy=True,
        slicesSet=[0.0,0.25,0.5,0.75],
    )
    mutableGameState['physics']['phi']=initPhi()
    mutableGameState['physics']['tau']=0
    (
        mutableGameState['physics']['phi'],
        mutableGameState['physics']['initEnergy'],_,_,_,_
    )=mutableGameState['physics']['integrator'].integrate(
        mutableGameState['physics']['phi']
    )
    mutableGameState['physics']['initEnergyThreshold']=(
        mutableGameState['physics']['initEnergy']-0.05*abs(
            mutableGameState['physics']['initEnergy']
        )
    )
    mutableGameState['lastWinningSpree']={
        'winner': None,
        'entered': 0,
    }
    return mutableGameState