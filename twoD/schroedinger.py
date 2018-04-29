#!/usr/bin/env python

'''
    schroedinger.py :
      two-dimensional study of integration of the
      Schroedinger equation
'''
from itertools import count
import time
import sys

from twoD.settings import (
    Nx,
    Ny,
    deltaLambdaX,
    deltaLambdaY,
)

from twoD.gui import (
    doPlot,
)

from twoD.wfunctions import (
    makeFakePhi,
)

from twoD.tools import (
    combineWFunctions,
    norm,
)

from twoD.dynamics import (
    evolve,
)

import numpy as np

def initPhi():
    # very fake for now
    phi=combineWFunctions(
        [
            makeFakePhi(Nx,Ny,0.25,0.75,0.2,amplitude=0.4),
            makeFakePhi(Nx,Ny,0.75,0.25,0.1,amplitude=0.8),
        ],
        deltaLambdaXY=deltaLambdaX*deltaLambdaY,
    )
    return phi

if __name__=='__main__':

    phi=initPhi()
    replotting=doPlot(phi)

    for i in count():
        n=norm(phi,deltaLambdaX*deltaLambdaY)
        phi=evolve(phi)
        doPlot(phi,replotting,title='Iter %06i, ND=%.4E (click to close)' % (i,n-1))
