'''
    settings.py : parameters.

    In all views, x is the HORIZONTAL view
    and y is the VERTICAL one, relative to the
    display shown on screen.

'''

import math
import pygame

# Physical parameters
LambdaX = 10
LambdaY = 10
Mu = 0.25#0.14

# discretisation parameters
Nx=64
Ny=64
deltaTau = 0.0004

periodicBCX=True
periodicBCY=True

# quantities derived from the above
deltaLambdaX=float(LambdaX)/float(Nx)
deltaLambdaY=float(LambdaY)/float(Ny)
deltaLambdaX2=deltaLambdaX**2
deltaLambdaY2=deltaLambdaY**2
waveNumber0=(2*math.pi/LambdaX,2*math.pi/LambdaY)

# display parameters
tileX=8
tileY=8
drawFreq=15
framesToDraw=None # None => forever

potentialColor=[180,0,0]

padIncrement=0.003
arrowKeyMap={
    pygame.K_LEFT:  (-padIncrement,0),
    pygame.K_RIGHT: (+padIncrement,0),
    pygame.K_UP:    (0,-padIncrement),
    pygame.K_DOWN:  (0,+padIncrement),
}
