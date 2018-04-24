'''
    settings.py : parameters,
'''

import math

# PHYSICAL PARAMETERS
#   in units of (the appropriate power of)
#   the electron mass m_e = 0.5 MeV/c^2
Lambda = 10

# low-res
Nx = 250#250#250
DeltaTau = 0.1# 0.0003

Mu = 0.5
PotV = 0.03
# quantities derived from the above
DeltaLambda=float(Lambda)/float(Nx)
DeltaLambda2=DeltaLambda**2
KineticFactor=-1.0/(2.0*float(Mu))
waveNumber0 = 2*math.pi/Lambda

periodicBC=True

# graphics options
drawFreq=1#50#60
