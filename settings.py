'''
    settings.py : parameters,
'''

# PHYSICAL PARAMETERS
#   in units of (the appropriate power of)
#   the electron mass m_e = 0.5 MeV/c^2
Lambda = 10
Nx = 350
DeltaTau = 0.000005
Mu = 0.5
PotV = 0.03
# quantities derived from the above
DeltaLambda=float(Lambda)/float(Nx)
DeltaLambda2=DeltaLambda**2
KineticFactor=-1.0/(2.0*float(Mu))

periodicBC=True

# graphics options
drawFreq=100
