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

from units import (
    toLength_fm,
)

reColorList=  ['#e71455','#9635fb']
imColorList=  ['#b26700','#00dcff']
mod2ColorList=['#FF0000','#0000ff']
potColor='#00C000'
zeroColor='#c0c0c0'
def doPlot(xs,phis,pots,title='',replotting=None):
    '''
        if replotting is None: creates the plot window.
        Else: refreshes the plot interactively using the handles
    '''
    if replotting is None:
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        physXs=[toLength_fm(i*Lambda/Nx) for i in xs]
        #
        phimod2={}
        phimax={}
        for iphi,phi in enumerate(phis):
            phimod2[iphi]=mod2(phi)
            phimax[iphi]=max(max(phimod2[iphi]),max(re(phi)),max(im(phi)))
        maxPots=max(pots) if max(pots)>0 else 1.0
        totalPhimax=max(phimax.values())
        scalePots=[p*totalPhimax/maxPots for p in pots]
        #
        plotZero, = ax.plot(physXs,[0]*Nx,'-',color=zeroColor)
        plotPot, = ax.plot(physXs,scalePots, '-',color=potColor,lineWidth=3)
        plotMod2={}
        plotRe={}
        plotIm={}
        for iphi,phi in enumerate(phis):
            plotMod2[iphi], = ax.plot(physXs, mod2(phi), '-',color=mod2ColorList[iphi],lineWidth=3)
            plotRe[iphi], = ax.plot(physXs, re(phi), '-',color=reColorList[iphi],lineWidth=1)
            plotIm[iphi], = ax.plot(physXs, im(phi), '-',color=imColorList[iphi],lineWidth=1)
        plt.xlabel('fm')
        plt.ylim((-totalPhimax,totalPhimax))
        replotStruct={
            'fig' : fig,
            'ax'  : ax,
            're'  : plotRe,
            'im'  : plotIm,
            'mod2': plotMod2,
            'pot' : plotPot,
            'totalPhimax': totalPhimax,
            'maxpots': maxPots,
        }
        return replotStruct
    else:
        scalePots=[p*replotting['totalPhimax']/replotting['maxpots'] for p in pots]
        for iphi,phi in enumerate(phis):
            replotting['re'][iphi].set_ydata(re(phi))
            replotting['im'][iphi].set_ydata(im(phi))
            replotting['mod2'][iphi].set_ydata(mod2(phi))
        replotting['pot'].set_ydata(scalePots)
        replotting['ax'].set_title(title)
        replotting['fig'].canvas.draw()
