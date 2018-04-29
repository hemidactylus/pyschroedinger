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

# discretisation parameters
Nx=90
Ny=90

# quantities derived from the above
deltaLambdaX=float(LambdaX)/float(Nx)
deltaLambdaY=float(LambdaY)/float(Ny)
deltaLambdaX2=deltaLambdaX**2
deltaLambdaY2=deltaLambdaY**2
waveNumberX0 = 2*math.pi/LambdaX
waveNumberY0 = 2*math.pi/LambdaY

# display parameters
tileX=6
tileY=6
