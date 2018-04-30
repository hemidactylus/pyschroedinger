'''
    dynamics.py : integration of the Schroedinger equation
'''

import numpy as np
from scipy.sparse import csr_matrix

from oneD.tools import (
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

class SparseMatrixRK4Integrator(WFIntegrator):
    '''
        RK4
        uses sparse matrices
        uses U=(1+H)^n
        does n timesteps at once
    '''
    def __init__(
        self,
        wfSize,
        deltaTau,
        deltaLambda,
        nIntegrationSteps,
        vPotential,
        periodicBC,
        mu,
    ):
        '''
            the evolution matrix U^nIntegrationSteps is prepared here
            for later usage
        '''
        self.nIntegrationSteps=nIntegrationSteps
        self.wfSize=wfSize
        self.periodicBC=periodicBC
        self.deltaTau=deltaTau
        self.deltaLambda=deltaLambda
        self.vPotential=vPotential
        self.mu=mu
        self.totalDeltaTau=self.nIntegrationSteps*self.deltaTau
        self._refreshEvoU()

    def _refreshEvoU(self):
        '''
            calculates the nIntegrationSteps evolution matrix
                U = (1+H)^nIntegrationSteps
            such that the nIntSteps evolution is given by
                phi -> U * phi
        '''
        self.evoU=csr_matrix(np.linalg.matrix_power(
            createRK4StepMatrixH(
                self.vPotential,
                self.deltaTau,
                self.deltaLambda,
                self.wfSize,
                self.periodicBC,
                self.mu
            )+np.diag(np.ones(self.wfSize)),
            self.nIntegrationSteps,
        ))

    def setPotential(self,vPotential):
        self.vPotential=vPotential
        self._refreshEvoU()

    def integrate(self,phi,nSteps):
        '''
            NO CHECKS are made whether nSteps matches self.nIntegrationSteps
            (it should!), for the sake of speed

            Given phi and nSteps, a tuple is returned:
                newPhi, normBias, timeIncrement
        '''
        newPhi=self.evoU.dot(phi)
        newNorm=norm(newPhi,self.deltaLambda)
        return (
            newPhi/newNorm,
            newNorm-1,
            self.totalDeltaTau,
        )

class RK4StepByStepIntegrator(WFIntegrator):
    '''
        RK4
        does not use matrices
        one timestep at a time (internally, for phi->phi)
    '''
    def __init__(
        self,
        wfSize,
        deltaTau,
        deltaLambda,
        nIntegrationSteps,
        vPotential,
        periodicBC,
        mu,
    ):
        '''
            nIntegrationSteps is discarded
        '''
        self.wfSize=wfSize
        self.periodicBC=periodicBC
        self.deltaTau=deltaTau
        self.deltaLambda=deltaLambda
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
            self.deltaLambda,
            self.kineticFactor,
            self.periodicBC,
        )
        k2 = evolutionOperator(
            phi+k1*self.halfDeltaTau,
            self.vPotential,
            self.deltaLambda,
            self.kineticFactor,
            self.periodicBC,
        )
        k3=evolutionOperator(
            phi+k2*self.halfDeltaTau,
            self.vPotential,
            self.deltaLambda,
            self.kineticFactor,
            self.periodicBC,
        )
        k4=evolutionOperator(
            phi+self.deltaTau*k3,
            self.vPotential,
            self.deltaLambda,
            self.kineticFactor,
            self.periodicBC,
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
        newNorm=norm(newPhi,self.deltaLambda)
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
        wfSize,
        deltaTau,
        deltaLambda,
        nIntegrationSteps,
        vPotential,
        periodicBC,
        mu,
    ):
        '''
            nIntegrationSteps is discarded
        '''
        self.wfSize=wfSize
        self.periodicBC=periodicBC
        self.deltaTau=deltaTau
        self.deltaLambda=deltaLambda
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
                    self.deltaLambda,
                    self.kineticFactor,
                    self.periodicBC,
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
        newNorm=norm(newPhi,self.deltaLambda)
        return (
            newPhi/newNorm,
            newNorm-1,
            self.deltaTau*nSteps,
        )

# general-purpose dynamic matrix utilities

def createRK4StepMatrixH(vPotential,deltaTau,deltaLambda,wfSize,periodicBC,mu):
    '''
        Creates the matrix H, encoding the whole rk process.
        H is such that for one deltaTau time step
            phi -> phi + H*phi
    '''
    sF=deltaTau*createEvolutionMatrixF(vPotential,wfSize,deltaLambda,periodicBC,mu)
    H=(sF+sF.dot(sF)/2.+sF.dot(sF).dot(sF)/6.+sF.dot(sF).dot(sF).dot(sF)/24.)
    return H

def createEvolutionMatrixF(vPotential,wfSize,deltaLambda,periodicBC,mu):
    '''
        returns a wfSize*wfSize matrix F,
            F = (i/2mu)(kinetic part)-i(v)
        defined so that the Schroedinger equation,
        discretised, reads
            d phi / d tau = F[phi]
    '''
    # the kinetic part
    kinPart=np.diag(2*np.ones(wfSize))
    for i in range(wfSize):
        kinPart[i,(i+1)%wfSize]=-1
        kinPart[(i+1)%wfSize,i]=-1
    if not periodicBC:
        kinPart[wfSize-1,0]=0
        kinPart[0,wfSize-1]=0
    # together with the potential is the final result
    mKinFactor=complex(0,1.0/(2.0*float(mu)*(deltaLambda**2)))
    return mKinFactor*kinPart+complex(0,-1)*np.diag(vPotential)

def evolutionOperator(Phi,vPotential,deltaLambda,kineticFactor,periodicBC):
    '''
        given wf and potential, (and using mu and lambda),
        evaluates F[phi] in
            delta phi/delta tau = F[phi]
        i.e.
            F = -i ( (/1(2mu)) delta2phi/deltaLambda2 + v*phi )
    '''
    if periodicBC:
        enlargedPhi=np.hstack([Phi[-1:],Phi,Phi[:1]])
        secondDerivative=kineticFactor*(2*Phi-enlargedPhi[:-2]-enlargedPhi[2:])/(deltaLambda**2)
    else:
        secondDerivative=np.hstack([
            complex(0),
            kineticFactor*(2*Phi[1:-1]-Phi[:-2]-Phi[2:])/(deltaLambda**2),
            complex(0),
        ])
    #
    minusI = complex(0,-1)
    F = minusI*(secondDerivative+vPotential*Phi)
    return F

def energy(Phi,vPotential,periodicBC,deltaLambda,mu):
    '''
        evaluates <phi|E|phi>, the adimensional
        version of <psi|E|psi>
    '''
    kineticFactor=-1.0/(2.0*float(mu))
    if periodicBC:
        enlargedPhi=np.hstack([Phi[-1:],Phi,Phi[:1]])
        secondDerivative=kineticFactor*(2*Phi-enlargedPhi[:-2]-enlargedPhi[2:])/(deltaLambda**2)
    else:
        secondDerivative=np.hstack([
            complex(0),
            kineticFactor*(2*Phi[1:-1]-Phi[:-2]-Phi[2:])/(deltaLambda**2),
            complex(0),
        ])
    #
    complexEn = sum(
        p.conjugate()*(d2+v*p)
        for d2,v,p in zip (secondDerivative,vPotential,Phi)
    )
    if abs(complexEn.imag) > 0.001*abs(complexEn.real):
        raise ValueError('Energy substantially complex: %f | %f' % (complexEn.real,complexEn.imag))
    return complexEn.real
