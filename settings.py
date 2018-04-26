'''
    settings.py : parameters,
'''

import math

from dynamics import (
    SparseMatrixRK4Integrator,
    RK4StepByStepIntegrator,
)

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
waveNumber0 = 2*math.pi/Lambda

periodicBC=True

# graphics/simulation options

# which integrator to compare
integratorMap={
    'RKspa': SparseMatrixRK4Integrator,
    # 'RKste': RK4StepByStepIntegrator,
}
# every drawFreq deltaTau updates is the screen refreshed
drawFreq=100
# how many frames to draw before stopping (None = forever)
framesToDraw=None
