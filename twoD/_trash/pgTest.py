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

    # to get 2x2 (or so) pixels, help from:
        https://gamedev.stackexchange.com/questions/96809/scaling-surface-changes-colors ?
'''

import pygame,sys
import numpy as np
import time
from pygame.locals import *

TILESIZE=2
MAPWIDTH=256
MAPHEIGHT=256


def myPalette(n):
    return [
        tuple([int(i*255/n+0.5)]*3)
        #[int(i*255.9/n),0,255-int(i*255.9/n)]
        for i in range(n)
    ]

pygame.init()
# SURF=pygame.display.set_mode(
window=pygame.display.set_mode(
    (
        MAPWIDTH*TILESIZE,
        MAPHEIGHT*TILESIZE,
    ),
    pygame.DOUBLEBUF,
    8,
)
screen=pygame.Surface((MAPWIDTH,MAPHEIGHT))#.convert()

pygame.display.set_palette(myPalette(256))

# a fixer?
for q in range(256):
    screen.set_palette_at(q,tuple([int(q*255/256.+0.5)]*3))

for q in range(256):
    print('%i -> %s' % (
        q,
        str(screen.get_palette_at(q))
    ))

# f=lambda xyp: xyp[2]
#0.5+(np.sin((((xyp[0]-0.5)**2+(xyp[1]-0.5)**2)**0.5)*np.pi*2+xyp[2]))*0.5

def makeF(p):
    a1=np.zeros((MAPWIDTH,MAPHEIGHT))
    for i in range(MAPWIDTH):
        for j in range(MAPHEIGHT):
            x=i*1.0/MAPWIDTH
            y=j*1.0/MAPHEIGHT
            a1[i][j]=i if j<200 else 127 #f((x,y,p))
    return a1

def evolve(a,p):
    # b=np.zeros((MAPWIDTH,MAPHEIGHT))
    # for i in range(MAPWIDTH):
    #     for j in range(MAPHEIGHT):
    #         b[i][j]=a[(i+1)%MAPWIDTH][(j+MAPHEIGHT-1)%MAPHEIGHT]
    # return b
    return makeF(p)

a1=makeF(0)
pixl_arr = (a1).astype(int)
# SURF = pygame.transform.scale(SURF,(2*MAPWIDTH,2*MAPHEIGHT))
old_surf = pygame.pixelcopy.make_surface(pixl_arr).convert()
for i in range(1000):
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
    a1=evolve(a1,i)
    # print('P=%i' % i)
    time.sleep(0.2)
    #
    pixl_arr = (a1).astype(int)
    # print('p_a %i' % pixl_arr[0][0])
    pygame.pixelcopy.array_to_surface(old_surf, pixl_arr)
    # old_surf=pygame.transform.scale(old_surf,(TILESIZE*MAPWIDTH,TILESIZE*MAPHEIGHT))
    screen.blit(old_surf, (0, 0))

    print(' '.join(str(e) for e in pixl_arr.transpose()[0]))

    pygame.transform.scale(screen, (TILESIZE*MAPWIDTH,TILESIZE*MAPHEIGHT), window)
    pygame.display.update()
    time.sleep(10)