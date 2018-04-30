'''
    dynamics.py : integration of the Schroedinger equation
'''

import numpy as np

from twoD.tools import (
    mod2,
    norm,
    re,
    im,
)

class WFIntegrator():
    def __init__(
        self,
        wfSize,
        deltaTau,
        deltaLambda,
        nIntegrationSteps,
        periodicBC,
        mu,
    ):
        raise NotImplementedError

    def setPotential(self,pot):
        raise NotImplementedError

    def integrate(self,phi,nSteps):
        raise NotImplementedError

class NaiveFiniteDifferenceIntegrator(WFIntegrator):
    '''
        Naive finite-difference integrator
        uses the simple discretised (adimensional) Schroedinger eq.
        one timestep at a time (internally, for phi->phi)
    '''
    def __init__(
        self,
        wfSizeX,
        wfSizeY,
        deltaTau,
        deltaLambdaX,
        deltaLambdaY,
        nIntegrationSteps,
        vPotential,
        periodicBCX,
        periodicBCY,
        mu,
    ):
        '''
            nIntegrationSteps is discarded
        '''
        self.wfSizeX=wfSizeX
        self.wfSizeY=wfSizeY
        self.periodicBCX=periodicBCX
        self.periodicBCY=periodicBCY
        self.deltaTau=deltaTau
        self.deltaLambdaX=deltaLambdaX
        self.deltaLambdaY=deltaLambdaY
        self.deltaLambdaXY=self.deltaLambdaX*self.deltaLambdaY
        self.halfDeltaTau=0.5*self.deltaTau
        self.vPotential=vPotential
        self.mu=mu
        # specials
        self.kineticFactor=-1.0/(2.0*float(self.mu))
        # not much else to do

    def setPotential(self,vPotential):
        self.vPotential=vPotential

    def _performSingleIntegrationStep(self,phi):
        '''
            does what the function name says
            and returns a new phi, over a single deltaTau.
            No normalisation is performed
        '''
        return np.array([
          p+self.deltaTau*dp
          for p,dp in zip(
                phi,
                evolutionOperator(
                    phi,
                    self.vPotential,
                    self.deltaLambdaX,
                    self.deltaLambdaY,
                    self.kineticFactor,
                    self.periodicBCX,
                    self.periodicBCY,
                ),
            )
        ])

    def integrate(self,phi,nSteps):
        '''
            Implements a simple integration,
            repeated nSteps times.
        '''
        newPhi=phi
        for _ in range(nSteps):
            newPhi=self._performSingleIntegrationStep(newPhi)
        newNorm=norm(newPhi,self.deltaLambdaXY)
        return (
            newPhi/newNorm,
            newNorm-1,
            self.deltaTau*nSteps,
        )

def evolutionOperator(Phi,vPotential,deltaLambdaX,deltaLambdaY,kineticFactor,periodicBCX,periodicBCY):
    if periodicBCX and periodicBCY:
        # x direction
        PV=np.vstack([[Phi[:][-1]],Phi[:][:],[Phi[:][0]]])
        PT=Phi.transpose()
        PADDED=np.vstack([[PT[-1][:]],PT[:][:],[PT[0][:]]])
        #
        DX=(2*Phi-PV[:-2]-PV[2:])/(deltaLambdaX**2)
        DY=((2*PT-PADDED[:-2]-PADDED[2:]).transpose())/(deltaLambdaY**2)
        a=1
        #
        secondDerivative=kineticFactor*(DX+DY)
    else:
        raise NotImplementedError('only periodic BC are supported')
    #
    minusI = complex(0,-1)
    F = minusI*(secondDerivative+vPotential*Phi)
    return F
