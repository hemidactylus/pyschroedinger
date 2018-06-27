'''
    interactiveSettings.py :
        interaction-specific config
'''

import pygame

padIncrement=0.03
fullArrowKeyMap={
    pygame.K_LEFT:  {
        'incr': (-padIncrement,0),
        'player': 0,
    },
    pygame.K_RIGHT: {
        'incr': (+padIncrement,0),
        'player': 0,
    },
    pygame.K_UP:    {
        'incr': (0,-padIncrement),
        'player': 0,
    },
    pygame.K_DOWN:  {
        'incr': (0,+padIncrement),
        'player': 0,
    },
    pygame.K_a:  {
        'incr': (-padIncrement,0),
        'player': 1,
    },
    pygame.K_d: {
        'incr': (+padIncrement,0),
        'player': 1,
    },
    pygame.K_w:    {
        'incr': (0,-padIncrement),
        'player': 1,
    },
    pygame.K_s:  {
        'incr': (0,+padIncrement),
        'player': 1,
    },
}

patchRadii=(0.08,0.08)
fieldBevelX=0.03
fieldBevelY=0.03

potWavefunctionDampingDivider=120000
potBorderWallHeight=8000
potPlayerPadHeight=10000

intPotentialColor=[0,180,90]
intPlayerColors=[
    [240,70,70],
    [50,50,180],
]
