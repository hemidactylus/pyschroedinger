'''
    settings.py : parameters.

    In all views, x is the HORIZONTAL view
    and y is the VERTICAL one, relative to the
    display shown on screen.

'''

import math

# Physical parameters
LambdaX = 10
LambdaY = 10
Mu = 0.2

# discretisation parameters
Nx=160
Ny=160
deltaTau = 0.0003

periodicBCX=True
periodicBCY=True

# quantities derived from the above
deltaLambdaX=float(LambdaX)/float(Nx)
deltaLambdaY=float(LambdaY)/float(Ny)
deltaLambdaX2=deltaLambdaX**2
deltaLambdaY2=deltaLambdaY**2
waveNumber0=(2*math.pi/LambdaX,2*math.pi/LambdaY)

# display parameters
tileX=4
tileY=4
drawFreq=20
framesToDraw=1000 # None => forever