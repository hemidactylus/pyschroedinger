# pyschroedinger

A game of __pong__ where the ball is not a classical particle, rather a
quantum-mechanical wavefunction.

**License**: [Creative Commons Attribution 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/). See [LICENSE.md](LICENSE.md) in this repository.

## The game

### How to play

Clone this repository, create a Python 3
virtual environment, e.g. called `qpong`,
install in it the packages specified in `requirements.txt` with

    pip install -r requirements.txt

and set the repository's root directory
in the virtual environment's import search path, e.g. with

    add2virtualenv .

In order to play the game, type

    ./game.py

and follow the on-screen instructions.

### Music and sound

Music for several states (playing, menu) and sound effects
for several events (victory, match-start countdown, etc...)
is loaded at game start in the appropriate directories
under `qpong/resources/music/*` and `qpong/resources/sound/*`.

Music must be in `mp3` format and sound in signed, PCM 16-bit `wav`
format. One can place as many files as desired in the subfolders: they will
all be used in the game, picking at random each time among the available choices.

### Changing in-code game settings

The game settings reside in the subdirectory `qpong` and are:

- `settings.py`, where the core physics is set;
- `interactiveSettings.py`, where game-specific features that go beyond the core physics engine are set.

Feel free to play with these two files.

More advanced tweaks are possible, such as changing the shape of the player pad,
the playing field base shape of the potential or the initial wavefunction configuration.
These and similar changes require a bit of understanding of how the code is structured.

## The physics

For more details, see the dedicated page about the [underlying physics](docs/physics.md).

The game is built upon a general integrator for the Schroedinger equation. Actually
there are several of them, one- and two- dimensional and with various features
(time-dependent vs. static potential, naive vs. Runge-Kutta integrator, etc).

In the game, a few small tweaks are introduced on top of the integration
to correct for effects that would make the game hardly playable (see below).

One- and two-dimensional "playground" setups, aside from the game itself,
are available to play and experiment with the core integrator engine, as
illustrated in the examples below. To play with them, go to either directory
`oneD` or `twoD` and, after playing with the directory's `settings.py`, type:

    ./schroedinger.py

### Examples

__Tunnel effect__: A (one-dimensional) Gaussian wave packet (mass is half that of the electron)
hits a finite potential barrier and tunnels through it (with periodic B.C.):

<img src="images/tunnel_oned.gif" alt="Unidimensional tunnel effect" style="width: 80%;"/>

__Two-slit experiment__: A two-dimensional "almost-plane wave" hits a very steep potential wall with two slits
and the portion of wave that goes through produces the famous interference pattern on the other side of the field.
With a particle of half the mass of the electron and a field roughly of side 4000 fm, the scene depicted here
spans about 0.000001 fs.
(After a while the motion of the wavefunction gets very messy: this is because, with fixed
boundary conditions in both directions, the borders reflect back the wave, which then starts interfering
with itself.)

<img src="images/double_slit_twod_1e-6fs.gif" alt="Two-dimensional double slit" style="width: 80%;"/>

(_Note_: to generate the frames for this example, the program was tweaked to display both the potential and
the wavefunction; even more crucial, due to my incomplete knowledge of `pygame`, was the choice to make without
the 8-bit color palette, using instead full RGB colors for the rendering of the image -- that seemed
to be the only way to get the right colors on the saved picture files.)

## Game-specific physics "tweaks"

In the game, the player control a "pad" that is, in fact, an island of high potential
in the system, whose position changes over time. This leads to two unpleasant
consequences that have to be addressed, at the cost of tweaking a bit the
quantum evolution of the system, to keep the game playable:

(1) Since the pad motion is discrete, it so happens that the pad slides under a
region where the wavefunction has a high value: this, effectively, raises the total
energy of the system in an unwarranted way, a fact which mostly manifests itself
as a growth of high-frequency components in the wavefunction (a rougher and rougher psi).
To keep this under control, a smoothing matrix, designed to kill high frequencies, is applied
to psi whenever, after the update iteration, the new total energy exceeds a threshold
set by the initial energy of the system.

(2) Another consequence of the discretised time steps is the fact that, when the pad
slides under a region with large psi, the latter is effectively "trapped" there (the pad having
a constant potential at its core. If one had infinitesimal time steps, the wave function
would be, correctly, pushed away by the gradient of the potential at the rim of the pads:
here, to avoid trapping large portions of the wave function within the pad, we apply a damping
factor at each iteration of type 

<img
  src="images/formulae/fml_pot-damping.svg"
/>

with v<sub>0</sub> chosen as large as possible as long as it does its job. Unfortunately,
this is a minor tweak that may hinder e.g. exploiting the tunnel effect in
some way throughout the game.

## Credits

## Todo

Refactor documentation: main (game + physics), physics, demo animations.
Restructure DOC/readme

wavefunction push-forward? how?

Deep refactoring of the qpong part: make it readable, more smaller modules!

Credits/info page: (1) fill it

symmetry of evolution: minor bias to the right remains (?),
strips for winning-checks.
It must all be symmetrical.

Critical review of all sound effects and music

A pool of initial wavefunction configurations at each match start?
