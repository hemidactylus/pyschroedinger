'''
    dynamics.py : integration of the Schroedinger equation
'''

import numpy as np
from scipy.sparse import csr_matrix

from twoD.tools import (
    mod2,
    norm,
    re,
    im,
)

from twoD.settings import (
    Nx,
    Ny,
)

class WFIntegrator():
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
        exactEnergy=False,
        slicesSet=None
    ):
        self.wfSizeX=wfSizeX
        self.wfSizeY=wfSizeY
        self.periodicBCX=periodicBCX
        self.periodicBCY=periodicBCY
        self.deltaTau=deltaTau
        self.deltaLambdaX=deltaLambdaX
        self.deltaLambdaY=deltaLambdaY
        self.nIntegrationSteps=nIntegrationSteps
        self.totalDeltaTau=self.deltaTau*self.nIntegrationSteps
        self.deltaLambdaXY=self.deltaLambdaX*self.deltaLambdaY
        self.vPotential=vPotential
        self.mu=mu
        self.exactEnergy=exactEnergy
        self.kineticFactor=-1.0/(2.0*float(self.mu))
        self.slices = None if slicesSet is None else [
            int(0.5+slFraction*self.wfSizeX*self.wfSizeY)
            for slFraction in sorted(slicesSet)
        ]
        if self.exactEnergy:
            self.energyCalculator=createEnergyCalculator(
                self.wfSizeX,
                self.wfSizeY,
                self.periodicBCX,
                self.periodicBCY,
                self.deltaLambdaX,
                self.deltaLambdaY,
                self.mu,
            )
        else:
            self.energyCalculator=None
        self.lastEnergy=None

    def setPotential(self,pot):
        raise NotImplementedError

    def integrate(self,phi):
        newPhi=self._baseIntegrate(phi)
        newNorm,sliceNorm=norm(newPhi,self.deltaLambdaXY,slices=self.slices)
        #
        if self.exactEnergy:
            energy=self.energyCalculator(phi,self.vPotential,self.lastEnergy)
        else:
            energy=complex(0,1)*(
                    newPhi.transpose().conjugate().dot( newPhi-phi )
                )/self.totalDeltaTau

        return (
            newPhi/newNorm,
            energy.real,
            abs(energy.imag)/abs(energy.real),
            newNorm-1,
            self.totalDeltaTau,
            sliceNorm,
        )

class VariablePotSparseRK4Integrator(WFIntegrator):
    '''
        RK4
        uses sparse matrices
        applies repeatedly the one-step evolution
        optimised for time-dependent potential:
            the components of the evolution are assembled live
    '''
    def __init__(self,**kwargs):
        WFIntegrator.__init__(self,**kwargs)
        # calculation of the free-particle dynamics part
        self.freeMatrix=createEvolutionMatrixF(
            None,
            self.wfSizeX,
            self.wfSizeY,
            self.deltaLambdaX,
            self.deltaLambdaY,
            self.periodicBCX,
            self.periodicBCY,
            self.mu
        )
        self.halfDeltaTau=0.5*self.deltaTau
        #
        self.setPotential(kwargs['vPotential'])

    def setPotential(self,vPotential):
        np.copyto(self.vPotential,vPotential)

    def _naiveEvolutionOperator(self,phi):
        '''
            uses the precomputed components to perform the
            basic computation of the time evolution
        '''
        return (
            (self.freeMatrix.dot(phi))-\
            complex(0,1)*self.vPotential*phi
        )

    def _performSingleRKStep(self,phi):
        '''
            does what the function name says
            and returns a new phi.
            No normalisation is performed
        '''
        k1 = self._naiveEvolutionOperator(phi)
        k2 = self._naiveEvolutionOperator(phi+k1*self.halfDeltaTau)
        k3=self._naiveEvolutionOperator(phi+k2*self.halfDeltaTau)
        k4=self._naiveEvolutionOperator(phi+self.deltaTau*k3)
        self.lastEnergy = complex(0,1)*phi.conjugate().dot(k1)
        return (phi+self.deltaTau*(k1+2*k2+2*k3+k4)/6.0)

    def _baseIntegrate(self,phi):
        '''
            Implements procedural RK4

            nSteps is used (even though it should match nIntegrationSteps)
            and the returned elapsedTime accordingly
        '''
        newPhi=phi
        for _ in range(self.nIntegrationSteps):
            newPhi=self._performSingleRKStep(newPhi)
        return newPhi

class SparseMatrixRK4Integrator(WFIntegrator):
    '''
        RK4
        uses sparse matrices
        uses U=(1+H)^n
        does n timesteps at once
    '''
    def __init__(self,**kwargs):
        WFIntegrator.__init__(self,**kwargs)
        self._refreshEvoU()

    def _refreshEvoU(self):
        '''
            calculates the nIntegrationSteps evolution matrix
                U = (1+H)^nIntegrationSteps
            such that the nIntSteps evolution is given by
                phi -> U * phi
        '''
        # we exploit the fact that csr_matrix has a __pow__ method
        # so we turn the one-step 1+H into a sparse and then
        # compute its nIntSteps-th power within the sparseness realm.
        oneStepMatrixOH=(
            createRK4StepMatrixH(
                self.vPotential,
                self.deltaTau,
                self.deltaLambdaX,
                self.deltaLambdaY,
                self.wfSizeX,
                self.wfSizeY,
                self.periodicBCX,
                self.periodicBCY,
                self.mu
            )+csr_matrix(np.diag(np.ones(self.wfSizeX*self.wfSizeY)))
        )
        self.evoU=oneStepMatrixOH**self.nIntegrationSteps

    def setPotential(self,vPotential):
        self.vPotential=vPotential
        self._refreshEvoU()

    def _baseIntegrate(self,phi):
        '''
            NO CHECKS are made whether nSteps matches self.nIntegrationSteps
            (it should!), for the sake of speed

            Given phi and nSteps, a tuple is returned:
                newPhi, normBias, timeIncrement
        '''
        return self.evoU.dot(phi)


class RK4StepByStepIntegrator(WFIntegrator):
    '''
        RK4
        does not use matrices
        one timestep at a time (internally, for phi->phi)
    '''
    def __init__(self,**kwargs):
        WFIntegrator.__init__(self,**kwargs)
        self.halfDeltaTau=0.5*self.deltaTau

    def setPotential(self,vPotential):
        self.vPotential=vPotential

    def _performSingleRKStep(self,phi):
        '''
            does what the function name says
            and returns a new phi.
            No normalisation is performed
        '''
        k1 = evolutionOperator(
            phi.reshape((Nx,Ny)),
            self.vPotential.reshape((Nx,Ny)),
            self.deltaLambdaX,
            self.deltaLambdaY,
            self.kineticFactor,
            self.periodicBCX,
            self.periodicBCY,
            self.wfSizeX,
            self.wfSizeY,
        ).reshape((Nx*Ny))
        k2 = evolutionOperator(
            (phi+k1*self.halfDeltaTau).reshape((Nx,Ny)),
            self.vPotential.reshape((Nx,Ny)),
            self.deltaLambdaX,
            self.deltaLambdaY,
            self.kineticFactor,
            self.periodicBCX,
            self.periodicBCY,
            self.wfSizeX,
            self.wfSizeY,
        ).reshape((Nx*Ny))
        k3=evolutionOperator(
            (phi+k2*self.halfDeltaTau).reshape((Nx,Ny)),
            self.vPotential.reshape((Nx,Ny)),
            self.deltaLambdaX,
            self.deltaLambdaY,
            self.kineticFactor,
            self.periodicBCX,
            self.periodicBCY,
            self.wfSizeX,
            self.wfSizeY,
        ).reshape((Nx*Ny))
        k4=evolutionOperator(
            (phi+self.deltaTau*k3).reshape((Nx,Ny)),
            self.vPotential.reshape((Nx,Ny)),
            self.deltaLambdaX,
            self.deltaLambdaY,
            self.kineticFactor,
            self.periodicBCX,
            self.periodicBCY,
            self.wfSizeX,
            self.wfSizeY,
        ).reshape((Nx*Ny))
        return (phi+self.deltaTau*(k1+2*k2+2*k3+k4)/6.0)

    def _baseIntegrate(self,phi):
        '''
            Implements procedural RK4

            nSteps is used (even though it should match nIntegrationSteps)
            and the returned elapsedTime accordingly
        '''
        newPhi=phi
        for _ in range(self.nIntegrationSteps):
            newPhi=self._performSingleRKStep(newPhi)
        return newPhi

class NaiveFiniteDifferenceIntegrator(WFIntegrator):
    '''
        Naive finite-difference integrator
        uses the simple discretised (adimensional) Schroedinger eq.
        one timestep at a time (internally, for phi->phi)
    '''
    def __init__(self,**kwargs):
        WFIntegrator.__init__(self,**kwargs)
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
                phi.reshape((Nx,Ny)),
                evolutionOperator(
                    phi.reshape((Nx,Ny)),
                    self.vPotential.reshape((Nx,Ny)),
                    self.deltaLambdaX,
                    self.deltaLambdaY,
                    self.kineticFactor,
                    self.periodicBCX,
                    self.periodicBCY,
                    self.wfSizeX,
                    self.wfSizeY,
                ),
            )
        ]).reshape((Nx*Ny))

    def _baseIntegrate(self,phi):
        '''
            Implements a simple integration,
            repeated nSteps times.
        '''
        newPhi=phi
        for _ in range(self.nIntegrationSteps):
            newPhi=self._performSingleIntegrationStep(newPhi)
        return newPhi

def createRK4StepMatrixH(
    vPotential,
    deltaTau,
    deltaLambdaX,
    deltaLambdaY,
    wfSizeX,
    wfSizeY,
    periodicBCX,
    periodicBCY,
    mu
):
    '''
        Creates the matrix H, encoding the whole rk process.
        H is such that for one deltaTau time step
            phi -> phi + H*phi
    '''
    sF=deltaTau*createEvolutionMatrixF(
        vPotential,
        wfSizeX,
        wfSizeY,
        deltaLambdaX,
        deltaLambdaY,
        periodicBCX,
        periodicBCY,
        mu
    )
    H=(sF+sF.dot(sF)/2.+sF.dot(sF).dot(sF)/6.+sF.dot(sF).dot(sF).dot(sF)/24.)
    return H

def createEvolutionMatrixF(
    vPotential,
    wfSizeX,
    wfSizeY,
    deltaLambdaX,
    deltaLambdaY,
    periodicBCX,
    periodicBCY,
    mu
):
    '''
        returns a (wfSizeX*wfSizeY) x (wfSizeX*wfSizeY) matrix F,
            F = (i/2mu)(kinetic part)-i(v)
        defined so that the Schroedinger equation,
        discretised, reads
            d phi / d tau = F[phi]

        Note: when the matrices [x][y] used here
        undergo a reshape->(Nx*Ny),
        the index map is:
            [x][y] -> x*Ny+y
    '''
    # the kinetic part
    fullSize=wfSizeX*wfSizeY
    indexer=lambda x,y,_Ny=wfSizeY: x*_Ny+y
    # the X- differences
    kinPartX=np.diag(2*np.ones(fullSize))
    for x in range(wfSizeX):
        for y in range(wfSizeY):
            tIdx=indexer(x,y)
            kinPartX[tIdx,indexer((x+1)%wfSizeX,y)]=-1
            kinPartX[indexer((x+1)%wfSizeX,y),tIdx]=-1
        if not periodicBCX:
            for y in [0,wfSizeY-1]:
                tIdx=indexer(x,y)
                kinPartX[tIdx,indexer((x+1)%wfSizeX,y)]=0
                kinPartX[indexer((x+1)%wfSizeX,y),tIdx]=0
    # the Y- differences
    kinPartY=np.diag(2*np.ones(fullSize))
    for y in range(wfSizeY):
        for x in range(wfSizeX):
            tIdx=indexer(x,y)
            kinPartY[tIdx,indexer(x,(y+1)%wfSizeY)]=-1
            kinPartY[indexer(x,(y+1)%wfSizeY),tIdx]=-1
        if not periodicBCY:
            for x in [0,wfSizeX-1]:
                tIdx=indexer(x,y)
                kinPartY[tIdx,indexer(x,(y+1)%wfSizeY)]=0
                kinPartY[indexer(x,(y+1)%wfSizeY),tIdx]=0
    # together with the potential is the final result
    mKinFactorX=complex(0,1.0/(2.0*float(mu)*(deltaLambdaX**2)))
    mKinFactorY=complex(0,1.0/(2.0*float(mu)*(deltaLambdaY**2)))
    if vPotential is not None:
        return csr_matrix(
            mKinFactorX*kinPartX+mKinFactorY*kinPartY+complex(0,-1)*np.diag(vPotential)
        )
    else:
        return csr_matrix(
            mKinFactorX*kinPartX+mKinFactorY*kinPartY
        )

def evolutionOperator(
    Phi,
    vPotential,
    deltaLambdaX,
    deltaLambdaY,
    kineticFactor,
    periodicBCX,
    periodicBCY,
    wfSizeX,
    wfSizeY
):
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

def makeSmoothingMatrix(wfSizeX,wfSizeY,periodicBCX,periodicBCY,smoothingMap=[((0,0),1.0)]):
    '''
        constructs a smoothing (csr sparse) matrix S for usage
        in killing high frequencies as:
            phi_smoothed = S . phi
    '''
    fullSize=wfSizeX*wfSizeY
    indexer=lambda x,y,_Ny=wfSizeY: x*_Ny+y
    # the X- differences
    smoother=np.zeros((fullSize,fullSize))
    smMapSum=sum(mpRule[1] for mpRule in smoothingMap)
    normSmMap=[(smPos,smVal/smMapSum) for smPos,smVal in smoothingMap]
    for x in range(wfSizeX):
        for y in range(wfSizeY):
            tIdx=indexer(x,y)
            for (posDx,posDy),smVal in normSmMap:
                oIdx=indexer((x+posDx+wfSizeX)%wfSizeX,(y+posDy+wfSizeY)%wfSizeY)
                smoother[tIdx,oIdx]=smVal
    return csr_matrix(
        smoother
    )

def createEnergyCalculator(
    wfSizeX,
    wfSizeY,
    periodicBCX,
    periodicBCY,
    deltaLambdaX,
    deltaLambdaY,
    mu,
):
    enCalcData={
        'wfSizeX':      wfSizeX,
        'wfSizeY':      wfSizeY,
        'periodicBCX':  periodicBCX,
        'periodicBCY':  periodicBCY,
        'deltaLambdaX': deltaLambdaX,
        'deltaLambdaY': deltaLambdaY,
    }
    iFreeEnPart=complex(0,1)*createEvolutionMatrixF(
        None,
        wfSizeX,
        wfSizeY,
        deltaLambdaX,
        deltaLambdaY,
        periodicBCX,
        periodicBCY,
        mu,
    )
    def _enCalculator(wf,pot,lastEnergy,_data=enCalcData,_iF0=iFreeEnPart):
        '''
            F = (i/2mu)(kinetic part)-i(v)

            F0 = (i/2mu)(kinetic part)

            en = deltaLambda * [ phi* ( (-1/2mu)d2/dlambda2 + v ) phi ]
               = deltaLambda * [ phi* ( i*F ) phi ]
               = deltaLambda * [ phi* ( i*F0 + v ) phi ]
        '''
        if lastEnergy is not None:
            thisEn=lastEnergy
        else:
            # slow, sluggish re-calculation: to be avoided when possible
            thisEn=wf.conjugate().dot((
                _iF0+ \
                csr_matrix(np.diag(pot))
            ).dot(wf))
            # here we *AVERAGE* the two deltaLambdas assuming no large asymmetries!
            # CAREFUL
        return thisEn*(_data['deltaLambdaX']+_data['deltaLambdaY'])/2
    return _enCalculator
