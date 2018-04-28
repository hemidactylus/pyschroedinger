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

TILESIZE=6
MAPWIDTH=100
MAPHEIGHT=80


def myPalette(n):
    return [
        # [int(i*255/n+0.5)]*3
        [int(i*255.9/n),0,255-int(i*255.9/n)]
        # [255,0,0] if i==0 else [0,255,0]
        for i in range(n)
    ]

pygame.init()
window=pygame.display.set_mode(
    (
        MAPWIDTH*TILESIZE,
        MAPHEIGHT*TILESIZE,
    ),
    pygame.DOUBLEBUF,
    8,
)

screen=pygame.Surface((MAPWIDTH,MAPHEIGHT))
pygame.display.set_palette(myPalette(256))
screen.set_palette(myPalette(256))

# # a fixer?
# for q in range(256):
#     # screen.set_palette_at(q,(255,255,255))
#     screen.set_palette_at(q,tuple([int(q*255/256.+0.5)]*3))

screen.convert()

# def makeA(arr,n):
#     for j in range(MAPHEIGHT):
#         for i in range(MAPWIDTH):
#             arr[i][j]=(j+i+n)%256

nparray=np.zeros((MAPWIDTH*TILESIZE,MAPHEIGHT*TILESIZE)).astype(int)
screenL = pygame.surfarray.make_surface(nparray).convert()

nparray=np.zeros((MAPWIDTH,MAPHEIGHT)).astype(int)
old_surf = pygame.surfarray.make_surface(nparray).convert()

f=lambda xyp: (np.sin((((xyp[0]-0.5)**2+(xyp[1]-0.5)**2)**0.5)*np.pi*2+xyp[2])**4.0)
def makeF(p):
    a1=np.zeros((MAPWIDTH,MAPHEIGHT))
    for i in range(MAPWIDTH):
        for j in range(MAPHEIGHT):
            x=i*1.0/(MAPWIDTH-1)
            y=j*1.0/(MAPHEIGHT-1)
            a1[i][j]=255*f((x,y,p))
    return a1.astype(int)

for i in range(1000):
    for event in pygame.event.get():
        if event.type==QUIT or event.type==MOUSEBUTTONDOWN:
            pygame.quit()
            sys.exit()


    # makeA(nparray,i)
    # for y in range(MAPHEIGHT):
    #     for x in range(MAPWIDTH):
    #         nparray[x][y]=(16*(x+y)+i)%256
    nparray=makeF(i/10)
    
    pygame.pixelcopy.array_to_surface(old_surf, nparray)

    # old_surf.fill(i % 255)
    # print('fill %i => %s' % (i%255, str(old_surf.get_at((0,0)))))

    # for y in range(MAPHEIGHT):
    #     for x in range(MAPWIDTH):
    #         print('x=%i,y=%i -> %s' % (x,y,old_surf.get_at((x,y))))

    #screen.blit(old_surf, (0, 0))

    pygame.transform.scale(old_surf, (TILESIZE*MAPWIDTH,TILESIZE*MAPHEIGHT), screenL)
    # pygame.transform.scale(screen, (TILESIZE*MAPWIDTH,TILESIZE*MAPHEIGHT), screenL)

    window.blit(screenL,(0,0))

    pygame.display.flip()
    time.sleep(0.001)
