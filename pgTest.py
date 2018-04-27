'''
    pgTest.py : adapted from
      http://usingpython.com/pygame-tilemaps/
    then later see
      https://www.pygame.org/docs/ref/pixelcopy.html
    and
      https://www.pygame.org/docs/ref/surface.html
    and perhaps
      https://stackoverflow.com/questions/36750306/using-python-how-can-i-display-a-matrix-of-rgb-values-in-a-window

    for the fast nparray to surface copying:
        https://stackoverflow.com/questions/30818367/how-to-present-numpy-array-into-pygame-surface#30970504
'''

import pygame,sys
import numpy as np
import time
from pygame.locals import *

TILESIZE=1
MAPWIDTH=100
MAPHEIGHT=80


def myPalette(n):
    return [
        [int(i*255.9/n),0,255-int(i*255.9/n)]
        for i in range(n)
    ]

pygame.init()
SURF=pygame.display.set_mode(
    (
        MAPWIDTH*TILESIZE,
        MAPHEIGHT*TILESIZE,
    ),
    pygame.DOUBLEBUF,
    8,
)

pygame.display.set_palette(myPalette(256))

f=lambda xy: np.exp(-(x-0.5)**2)*abs(np.cos(15*y**2+9*x**2))
N=20
a1=np.zeros((MAPWIDTH,MAPHEIGHT))
for i in range(MAPWIDTH):
    for j in range(MAPHEIGHT):
        x=i*1.0/MAPWIDTH
        y=j*1.0/MAPHEIGHT
        a1[i][j]=f((x,y))

def evolve(a):
    b=np.zeros((MAPWIDTH,MAPHEIGHT))
    for i in range(MAPWIDTH):
        for j in range(MAPHEIGHT):
            b[i][j]=a[(i+1)%MAPWIDTH][(j+MAPHEIGHT-1)%MAPHEIGHT]
    return b

mkCol=lambda n: int(n*255.9)

pixl_arr = (255*a1).astype(int)
old_surf = pygame.pixelcopy.make_surface(pixl_arr)
for i in range(1000):
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
    a1=evolve(a1)
    #
    pixl_arr = (255*a1).astype(int)
    pygame.pixelcopy.array_to_surface(SURF, pixl_arr)
    SURF.blit(SURF, (0, 0))
    pygame.display.update()
