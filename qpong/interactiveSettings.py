'''
    interactiveSettings.py :
        interaction-specific config
'''

import pygame

padIncrement=0.03
fullArrowKeyMap={
    pygame.K_LEFT:  {
        'incr': (-padIncrement,0),
        'origPlayer': 0,
    },
    pygame.K_RIGHT: {
        'incr': (+padIncrement,0),
        'origPlayer': 0,
    },
    pygame.K_UP:    {
        'incr': (0,-padIncrement),
        'origPlayer': 0,
    },
    pygame.K_DOWN:  {
        'incr': (0,+padIncrement),
        'origPlayer': 0,
    },
    pygame.K_a:  {
        'incr': (-padIncrement,0),
        'origPlayer': 1,
    },
    pygame.K_d: {
        'incr': (+padIncrement,0),
        'origPlayer': 1,
    },
    pygame.K_w:    {
        'incr': (0,-padIncrement),
        'origPlayer': 1,
    },
    pygame.K_s:  {
        'incr': (0,+padIncrement),
        'origPlayer': 1,
    },
}

patchRadii=(0.08,0.08)
patchThickness=0.01
fieldBevelX=0.03
fieldBevelY=0.02
halfFieldArtifactWidth=0.05

potWavefunctionDampingDivider=20000
potBorderWallHeight=8000
potPlayerPadHeight=10000

intPotentialColor=[0,180,90]
intPlayerColors=[
    [240,70,70],
    [50,50,180],
]

# display parameters
tileX=10
tileY=10
drawFreq=5
potentialColor=[0,180,90]

labelFontSize=20
titleFontSize=100

panelBackgroundColor=170
panelForegroundColor=(80,100,50)
screenForegroundColor=(232,232,232)

# higher = harder to score a point
winningFraction=0.45

maxFrameRate=36 # frames/sec - when playing

panelHeight=80 # pixels

# do we use the global matrix once-allocated repository?
# (True = some speedup)
useMRepo=True

# on-screen countdown before match starts
matchCountdownSteps=3
matchCountdownSpan=0.5

# still-screen after player scores
endMatchStillTime=1.0
# still-screen after whole play finishes
endPlayStillTime=2.5

# iterations in a row in the 'winning' position for a player
winningSpreeNumIterations=54
# fractions of closeness to trigger danger warnings
aboutToWinDangerSignSteps=(0.33,0.67)

# how many points a player must score to win the play
defaultMatchesToWinAPlay=2
maximumMatchesToWinAPlay=30

defaultSoundActive=True