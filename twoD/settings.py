'''
    settings.py : parameters.

    In all views, x is the HORIZONTAL view
    and y is the VERTICAL one, relative to the
    display shown on screen.

'''

import math
import pygame

# Physical parameters
LambdaX = 1
LambdaY = 1
Mu = 0.25#0.14

# discretisation parameters
# Nx=36
# Ny=36
Nx=64
Ny=64
# deltaTau = 0.000005
deltaTau = 0.000003

periodicBCX=False
periodicBCY=False

# quantities derived from the above
deltaLambdaX=float(LambdaX)/float(Nx)
deltaLambdaY=float(LambdaY)/float(Ny)
deltaLambdaX2=deltaLambdaX**2
deltaLambdaY2=deltaLambdaY**2
waveNumber0=(2*math.pi/LambdaX,2*math.pi/LambdaY)

# display parameters
tileX=8
tileY=8
# drawFreq=50
drawFreq=5
framesToDraw=1000#None # None => forever

potentialColor=[0,180,90]
