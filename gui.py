'''
    gui.py : handles the GUI and the visualisation
    of the wavefunction as time passes
'''

import matplotlib.pyplot as plt

from settings import (
    xSize,
    xSteps,
)
from tools import (
    mod2,
    re,
    im,
)

def doPlot(xs,psis,pots,title='',replotting=None):
    '''
        if replotting is None: creates the plot window.
        Else: refreshes the plot interactively using the handles
    '''
    if replotting is None:
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        physXs=[i*xSize/xSteps for i in xs]
        maxPots=max(pots) if max(pots)>0 else 1.0
        scalePots=[p*0.2/maxPots for p in pots]
        plotPot, = ax.plot(physXs,scalePots, 'b-',lineWidth=3)
        plotMod2, = ax.plot(physXs, mod2(psis), 'k-',lineWidth=3)
        plotRe, = ax.plot(physXs, re(psis), 'r-',lineWidth=1)
        plotIm, = ax.plot(physXs, im(psis), 'g-',lineWidth=1)
        plt.ylim((-0.24,0.24))
        replotStruct={
            'fig' : fig,
            'ax'  : ax,
            're'  : plotRe,
            'im'  : plotIm,
            'mod2': plotMod2,
            'pot' : plotPot,
        }
        return replotStruct
    else:
        replotting['re'].set_ydata(re(psis))
        replotting['im'].set_ydata(im(psis))
        replotting['mod2'].set_ydata(mod2(psis))
        replotting['pot'].set_ydata(pots)
        replotting['ax'].set_title(title)
        replotting['fig'].canvas.draw()
