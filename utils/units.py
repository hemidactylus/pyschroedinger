'''
    units.py : tools to restore physical units to quantities
'''

m_e = 0.511 # MeV/c^2
hbarc = 197.0 # Mev*fm
c = 3.e8 # fm/fs

def toLength_fm(aLambda):
    '''
        given an adimensional length,
        fermi are returned
    '''
    return aLambda*hbarc/m_e

def toTime_fs(aTau):
    '''
        same for time
    '''
    return aTau*hbarc/(c*m_e)

def toEnergy_MeV(aE):
    '''
        energy in MeV
    '''
    return aE*m_e

def toMass_MeV_overC2(mu):
    return m_e*mu
