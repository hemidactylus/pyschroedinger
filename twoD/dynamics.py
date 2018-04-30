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

class RK4StepByStepIntegrator(WFIntegrator):
    '''
        RK4
        does not use matrices
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

    def _performSingleRKStep(self,phi):
        '''
            does what the function name says
            and returns a new phi.
            No normalisation is performed
        '''
        k1 = evolutionOperator(
            phi,
            self.vPotential,
            self.deltaLambdaX,
            self.deltaLambdaY,
            self.kineticFactor,
            self.periodicBCX,
            self.periodicBCY,
            self.wfSizeX,
            self.wfSizeY,
        )
        k2 = evolutionOperator(
            phi+k1*self.halfDeltaTau,
            self.vPotential,
            self.deltaLambdaX,
            self.deltaLambdaY,
            self.kineticFactor,
            self.periodicBCX,
            self.periodicBCY,
            self.wfSizeX,
            self.wfSizeY,
        )
        k3=evolutionOperator(
            phi+k2*self.halfDeltaTau,
            self.vPotential,
            self.deltaLambdaX,
            self.deltaLambdaY,
            self.kineticFactor,
            self.periodicBCX,
            self.periodicBCY,
            self.wfSizeX,
            self.wfSizeY,
        )
        k4=evolutionOperator(
            phi+self.deltaTau*k3,
            self.vPotential,
            self.deltaLambdaX,
            self.deltaLambdaY,
            self.kineticFactor,
            self.periodicBCX,
            self.periodicBCY,
            self.wfSizeX,
            self.wfSizeY,
        )
        return phi+self.deltaTau*(k1+2*k2+2*k3+k4)/6.0

    def integrate(self,phi,nSteps):
        '''
            Implements procedural RK4

            nSteps is used (even though it should match nIntegrationSteps)
            and the returned elapsedTime accordingly
        '''
        newPhi=phi
        for _ in range(nSteps):
            newPhi=self._performSingleRKStep(newPhi)
        newNorm=norm(newPhi,self.deltaLambdaXY)
        return (
            newPhi/newNorm,
            newNorm-1,
            self.deltaTau*nSteps,
        )

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
                    self.wfSizeX,
                    self.wfSizeY,
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

def evolutionOperator(Phi,vPotential,deltaLambdaX,deltaLambdaY,kineticFactor,periodicBCX,periodicBCY,wfSizeX,wfSizeY):
    if periodicBCX:
        largePhiX=np.vstack([[Phi[:][-1]],Phi[:][:],[Phi[:][0]]])
        der2X=(2*Phi-largePhiX[:-2]-largePhiX[2:])/(deltaLambdaX**2)
    else:
        zX=np.zeros((1,wfSizeX),complex)
        der2X=np.vstack([zX,2*Phi[1:-1]-Phi[:-2]-Phi[2:],zX])/(deltaLambdaX**2)
    #
    PhiT=Phi.transpose()
    if periodicBCX and periodicBCY:
        largePhiYT=np.vstack([[PhiT[-1][:]],PhiT[:][:],[PhiT[0][:]]])
        der2Y=((2*PhiT-largePhiYT[:-2]-largePhiYT[2:]).transpose())/(deltaLambdaY**2)
    else:
        zY=np.zeros((1,wfSizeY),complex)
        der2Y=np.vstack([zY,2*PhiT[1:-1]-PhiT[:-2]-PhiT[2:],zY]).transpose()/(deltaLambdaY**2)
    #
    secondDerivative=kineticFactor*(der2X+der2Y)
    #
    minusI = complex(0,-1)
    F = minusI*(secondDerivative+vPotential*Phi)
    return F
