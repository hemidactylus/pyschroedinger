'''
    dynamics.py : integration of the Schroedinger equation
'''

import numpy as np
from scipy.sparse import csr_matrix

from settings import (
    deltaLambda2,
    kineticFactor,
    periodicBC,
    Nx,
    Mu,
)

from tools import (
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
        nIntegrationSteps,
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
        nIntegrationSteps,
        vPotential,
    ):
        '''
            the evolution matrix U^nIntegrationSteps is prepared here
            for later usage
        '''
        self.nIntegrationSteps=nIntegrationSteps
        self.wfSize=wfSize
        self.deltaTau=deltaTau
        self.vPotential=vPotential
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
            createRK4StepMatrixH(self.vPotential,self.deltaTau)+np.diag(np.ones(self.wfSize)),
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
        newNorm=norm(newPhi)
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
        nIntegrationSteps,
        vPotential,
    ):
        '''
            the evolution matrix U^nIntegrationSteps is prepared here
            for later usage

            nIntegrationSteps is discarded
        '''
        self.wfSize=wfSize
        self.deltaTau=deltaTau
        self.halfDeltaTau=0.5*self.deltaTau
        self.vPotential=vPotential
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
        )
        k2 = evolutionOperator(
            phi+k1*self.halfDeltaTau,
            self.vPotential,
        )
        k3=evolutionOperator(
            phi+k2*self.halfDeltaTau,
            self.vPotential,
        )
        k4=evolutionOperator(
            phi+self.deltaTau*k3,
            self.vPotential,
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
        newNorm=norm(newPhi)
        return (
            newPhi/newNorm,
            newNorm-1,
            self.deltaTau*nSteps,
        )

# general-purpose dynamic matrix utilities

def createRK4StepMatrixH(vPotential,deltaTau):
    '''
        Creates the matrix H, encoding the whole rk process.
        H is such that for one deltaTau time step
            phi -> phi + H*phi
    '''
    sF=deltaTau*createEvolutionMatrixF(vPotential)
    H=(sF+sF.dot(sF)/2.+sF.dot(sF).dot(sF)/6.+sF.dot(sF).dot(sF).dot(sF)/24.)
    return H

def createEvolutionMatrixF(vPotential):
    '''
        returns a Nx*Nx matrix F,
            F = (i/2mu)(kinetic part)-i(v)
        defined so that the Schroedinger equation,
        discretised, reads
            d phi / d tau = F[phi]
    '''
    # the kinetic part
    kinPart=np.diag(2*np.ones(Nx))
    for i in range(Nx):
        kinPart[i,(i+1)%Nx]=-1
        kinPart[(i+1)%Nx,i]=-1
    if not periodicBC:
        kinPart[Nx-1,0]=0
        kinPart[0,Nx-1]=0
    # together with the potential is the final result
    mKinFactor=complex(0,1.0/(2.0*float(Mu)*deltaLambda2))
    return mKinFactor*kinPart+complex(0,-1)*np.diag(vPotential)

# still check that this does not read globals
def evolutionOperator(Phi,vPotential):
    '''
        given wf and potential, (and using mu and lambda),
        evaluates F[phi] in
            delta phi/delta tau = F[phi]
        i.e.
            F = -i ( (/1(2mu)) delta2phi/deltaLambda2 + v*phi )
    '''
    if periodicBC:
        enlargedPhi=np.hstack([Phi[-1:],Phi,Phi[:1]])
        secondDerivative=kineticFactor*(2*Phi-enlargedPhi[:-2]-enlargedPhi[2:])/deltaLambda2
    else:
        secondDerivative=np.hstack([
            complex(0),
            kineticFactor*(2*Phi[1:-1]-Phi[:-2]-Phi[2:])/deltaLambda2,
            complex(0),
        ])
    #
    minusI = complex(0,-1)
    F = minusI*(secondDerivative+vPotential*Phi)
    return F

# legacy stuff to refactor

# def integrate(Phi,vPotential,DeltaTau, iniTau):
#     '''
#         returns the new Phi after DeltaTau (and other things)
#     '''

#     newPhi = Phi+DeltaTau*evolutionOperator(Phi,vPotential)
#     newNorm=norm(newPhi)
#     #
#     return newPhi/newNorm, newNorm-1, iniTau+DeltaTau

def energy(Phi,vPotential):
    '''
        evaluates <phi|E|phi>, the adimensional
        version of <psi|E|psi>
    '''
    if periodicBC:
        enlargedPhi=np.hstack([Phi[-1:],Phi,Phi[:1]])
        secondDerivative=kineticFactor*(2*Phi-enlargedPhi[:-2]-enlargedPhi[2:])/deltaLambda2
    else:
        secondDerivative=np.hstack([
            complex(0),
            kineticFactor*(2*Phi[1:-1]-Phi[:-2]-Phi[2:])/deltaLambda2,
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