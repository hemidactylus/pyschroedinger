'''
    gui.py : handles the GUI and the visualisation
    of the wavefunction as time passes
'''

import matplotlib.pyplot as plt

from oneD.settings import (
    Lambda,
    Nx,
)
from oneD.tools import (
    mod2,
    re,
    im,
)

from utils.units import (
    toLength_fm,
)

reColorList=  ['#e71455','#9635fb','#b7f935']
imColorList=  ['#b26700','#00dcff','#73ccb2']
mod2ColorList=['#FF0000','#0000ff','#00881d']
potColor='#00C000'
zeroColor='#c0c0c0'
def doPlot(xs,phiMap,pots,title='',replotting=None,photoIndex=None):
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
        for iphi,(phiName,phi) in enumerate(sorted(phiMap.items())):
            phimod2[phiName]=mod2(phi)
            phimax[phiName]=max(max(phimod2[phiName]),max(re(phi)),max(im(phi)))
        maxPots=max(pots) if max(pots)>0 else 1.0
        totalPhimax=max(phimax.values())
        scalePots=[p*totalPhimax/maxPots for p in pots]
        #
        plotZero, = ax.plot(physXs,[0]*Nx,'-',color=zeroColor)
        plotPot, = ax.plot(physXs,scalePots, '-',color=potColor,lineWidth=3)
        plotMod2={}
        plotRe={}
        plotIm={}
        for iphi,(phiName,phi) in enumerate(sorted(phiMap.items())):
            plotMod2[phiName], = ax.plot(physXs, mod2(phi), '-',color=mod2ColorList[iphi],lineWidth=3)
            plotRe[phiName], = ax.plot(physXs, re(phi), '-',color=reColorList[iphi],lineWidth=1)
            plotIm[phiName], = ax.plot(physXs, im(phi), ':',color=imColorList[iphi],lineWidth=1)
        plt.xlabel('fm')
        plt.ylim((-totalPhimax,totalPhimax))
        ax.set_title(title,fontsize=10,family='monospace')
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
        if photoIndex is not None:
            print('saving %i' % photoIndex)
            replotStruct['fig'].set_size_inches(4,2.8)
            replotStruct['fig'].savefig('frame_%06i.png' % photoIndex,bbox_inches='tight')
        return replotStruct
    else:
        scalePots=[p*replotting['totalPhimax']/replotting['maxpots'] for p in pots]
        for iphi,(phiName,phi) in enumerate(sorted(phiMap.items())):
            replotting['re'][phiName].set_ydata(re(phi))
            replotting['im'][phiName].set_ydata(im(phi))
            replotting['mod2'][phiName].set_ydata(mod2(phi))
        replotting['pot'].set_ydata(scalePots)
        replotting['ax'].set_title(title,fontsize=10,family='monospace')
        replotting['fig'].canvas.draw()
        if photoIndex is not None:
            print('saving %i' % photoIndex)
            replotting['fig'].set_size_inches(4,2.8)
            replotting['fig'].savefig('frame_%06i.png' % photoIndex,bbox_inches='tight')
