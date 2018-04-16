'''
    gui.py : handles the GUI and the visualisation
    of the wavefunction as time passes
'''

import matplotlib.pyplot as plt

from settings import (
    Lambda,
    Nx,
)
from tools import (
    mod2,
    re,
    im,
)

def doPlot(xs,phis,pots,title='',replotting=None):
    '''
        if replotting is None: creates the plot window.
        Else: refreshes the plot interactively using the handles
    '''
    if replotting is None:
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        physXs=[i*Lambda/Nx for i in xs]
        #
        phimod2=mod2(phis)
        phimax=max(phimod2)
        maxPots=max(pots) if max(pots)>0 else 1.0
        scalePots=[p*phimax/maxPots for p in pots]
        #
        plotZero = ax.plot(physXs,[0]*Nx,'-',color='#c0c0c0')
        plotPot, = ax.plot(physXs,scalePots, 'b-',lineWidth=3)
        plotMod2, = ax.plot(physXs, mod2(phis), 'k-',lineWidth=3)
        plotRe, = ax.plot(physXs, re(phis), 'r-',lineWidth=1)
        plotIm, = ax.plot(physXs, im(phis), 'g-',lineWidth=1)
        plt.ylim((-phimax,phimax))
        replotStruct={
            'fig' : fig,
            'ax'  : ax,
            're'  : plotRe,
            'im'  : plotIm,
            'mod2': plotMod2,
            'pot' : plotPot,
            'phimax': phimax,
            'maxpots': maxPots,
        }
        return replotStruct
    else:
        scalePots=[p*replotting['phimax']/replotting['maxpots'] for p in pots]
        replotting['re'].set_ydata(re(phis))
        replotting['im'].set_ydata(im(phis))
        replotting['mod2'].set_ydata(mod2(phis))
        replotting['pot'].set_ydata(scalePots)
        replotting['ax'].set_title(title)
        replotting['fig'].canvas.draw()
