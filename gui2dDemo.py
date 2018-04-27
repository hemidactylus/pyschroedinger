'''
    gui2dDemo.py
'''

import numpy as np
import matplotlib.pyplot as plt

import time

if __name__=='__main__':

    print('INIT')

    f=lambda xy: np.exp(-(x-0.5)**2)*abs(np.cos(15*y**2+9*x**2))
    N=20
    a1=np.zeros((N,N))
    for i in range(N):
        for j in range(N):
            x=i*1.0/N
            y=j*1.0/N
            a1[i][j]=f((x,y))

    def evolve(a):
        return a*a

    plt.ion()
    fig=plt.figure(figsize=(10,10))

    ax = fig.add_subplot(111)

    hmap=ax.imshow(a1,cmap='brg')

    fig.canvas.draw()

    for i in range(50):

        a1=evolve(a1)

        hmap.set_array(a1)
        fig.canvas.draw() 
        time.sleep(0.05)
