'''
    potentials.py
'''

from functools import reduce
import numpy as np
import math

def freeParticlePotential(Nx,Ny):
    return np.zeros((Nx,Ny),dtype=float).reshape((Nx*Ny))

def ellipticHolePotential(Nx,Ny,pPos,pRadius,pThickness,vIn,vOut, reshape=True):
    '''
        a plateau, of elliptic shape, with a steepness of borders;
        center and values of the potential in and out are provided

        pThickness is a *scalar* and appilies after the radiusization,
        i.e. in scale where the border is at 'radius one'

    '''
    center=pPos
    radius=pRadius
    thickness=pThickness
    unsubPot=np.zeros((Nx,Ny),dtype=float)

    #
    for x in range(Nx):
        for y in range(Ny):
            _x=(x/(Nx-1))
            _y=(y/(Ny-1))
            _rho=((((_x-center[0])/radius[0])**2)+(((_y-center[1])/radius[1])**2))**0.5
            unsubPot[x][y]=vOut+(vIn-vOut)*((1+math.tanh((1-_rho)/thickness))/2)
    if reshape:
        return unsubPot.reshape((Nx*Ny))
    else:
        return unsubPot

def rectangularHolePotential(Nx,Ny,pPos,pThickness,vIn,vOut):
    '''
        a "step" i.e. a rectangular area of low pot
        (vIn) surrounded by high vOut through
        finite-thickness(x,y) rising edges

        pPos is a rectangle i.e. (x- and y- of upper left, width, height)
        in 0-1 units.
    '''
    topX=pPos[0]
    topY=pPos[1]
    botX=pPos[0]+pPos[2]
    botY=pPos[1]+pPos[3]
    #
    thickness=(pThickness[0]*Nx,pThickness[1]*Ny)
    #
    unsubPot=np.zeros((Nx,Ny),dtype=float)

    #
    for x in range(Nx):
        for y in range(Ny):
            _x=(x/(Nx-1))
            _y=(y/(Ny-1))
            # which one is the leading distance here?
            leadDistance=min(
                [
                    (_x-topX)/thickness[0],
                    (_y-topY)/thickness[1],
                    (botX-_x)/thickness[0],
                    (botY-_y)/thickness[1],
                ],
            )
            unsubPot[x][y]=vOut+(vIn-vOut)*((1+math.tanh(leadDistance))/2)
    return unsubPot.reshape((Nx*Ny))

def harmonicPotential(pPos,weights,Nx,Ny):
    '''
        generates a potential for 'harmonic',
        with "elliptical shape"
    '''
    unsubPot=np.zeros((Nx,Ny),dtype=float)
    for x in range(Nx):
        for y in range(Ny):
            _x=(x/(Nx-1))
            _y=(y/(Ny-1))
            unsubPot[x][y]=(weights[0]*(_x-pPos[0])**2)+(weights[1]*(_y-pPos[1])**2)
    return unsubPot.reshape((Nx*Ny))
