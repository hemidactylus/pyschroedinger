'''
    settings.py : parameters,
'''

import math

# PHYSICAL PARAMETERS
#   in units of (the appropriate power of)
#   the electron mass m_e = 0.5 MeV/c^2
Lambda = 10
Mu = 0.5

# discretisation parameters
Nx = 150
deltaTau = 0.0003

# quantities derived from the above
deltaLambda=float(Lambda)/float(Nx)
deltaLambda2=deltaLambda**2
kineticFactor=-1.0/(2.0*float(Mu))
waveNumber0 = 2*math.pi/Lambda

periodicBC=True

# graphics/simulation options
drawFreq=100
framesToDraw=None # None=forever
