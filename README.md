# pyschroedinger

A playground to learn something about numerical integration of the Schroedinger equation

## Get it running

Clone the repo, create the virtualenv
(with python3) and set the repo's root
dir into the path of the virtualenv.

Then go to either `oneD` or `twoD` directories, start

    ./schroedinger.py

and enjoy the show.

You can alter the initial wavefunction/potential by playing with the `initPhi`
and `initPot` functions in `schroedinger.py`, and you can tweak more fundamental
settings (time interval, grid size, boundary conditions, and so on) in `settings.py`.

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

## To do

A variable-pot version of the sparse integrator:
  - keeps the pot separately, calculates the dynamics+id part once
    in order to reapply the potential very time as a vector * vector (componentwise)
  - does NOT compute expensive powers of the OH matrix, applies several time
    the sparse one and that's it.
      FOR ONE TIMESTEP:
        phi = (1+H) phiO = (1+dyn+pot) phiO
      keep 1+dyn = D as a csr matrix
      and pot as a VECTOR
        phi = (D+V) phiO = D * phiO + V * phiO
      where the first * is (csr)matrix and the second is vector-vector.

Better calculation of the particle energy (pO=pOld, a dt ago):

(idea) <p|E|p> = <p|H|p> = ih <p|dp>/dt = ih <p| (|p>-|pO>) /dt
  = ih/dt [ <p|p> - <p|pO> ] = ih ( 1 - <p|pO> ) / dt


## Units

We choose natural units and set <img
  src="https://latex.codecogs.com/svg.latex?\hbar{\cdot}c=\hbar=c=1"
/>, so to recover the ordinary units:

<img
  src="https://latex.codecogs.com/svg.latex?\hbar=200~\frac{\mathrm{MeV~fm}}{c}"
/>

<img
  src="https://latex.codecogs.com/svg.latex?\hbar{c}=200~\mathrm{MeV}~\mathrm{fm}~\Rightarrow~1~\mathrm{fm}=\frac{\hbar{c}}{200~\mathrm{MeV}}"
/>

<img
  src="https://latex.codecogs.com/svg.latex?c=3\cdot{10}^{8}~\mbox{m/s}~\Rightarrow~1~\mathrm{fs}=1.5\cdot{10}^6\frac{\hbar}{\mbox{MeV}}"
/>

### Space and time

We work in a box of size L and proceed by time steps &Delta;t (in physical units).
The length of the box is divided into N<sub>x</sub> discrete intervals.

### Dimensions

Since the norm of Psi has to be a number, <img
  src="https://latex.codecogs.com/svg.latex?\int|\Psi|^2\mathrm{d}^dx=[1]"
/> implies:

<img
  src="https://latex.codecogs.com/svg.latex?[\Psi]=\mathrm{fm}^{-d/2}=\mathrm{MeV}^{d/2}"
/>

Now for the units of the potential V (in one dimension for brevity):

<img
  src="https://latex.codecogs.com/svg.latex?i\hbar\frac{\mathrm{d}\Psi}{\mathrm{d}t}=-\frac{\hbar^2}{2m}\frac{\mathrm{d}^2\Psi}{\mathrm{d}x^2}+V\Psi"
/>

means

<img
  src="https://latex.codecogs.com/svg.latex?\frac{\mathrm{MeV}\cdot{fm}}{c}\cdot\frac{1}{\mathrm{fm/c}}\cdot\mathrm{MeV}^{d/2}=\frac{\mathrm{MeV}^2\mathrm{fm}^2}{c^2}\frac{c^2}{\mathrm{MeV}}\frac{\mathrm{MeV}^{d/2}}{\mathrm{fm}^2}+[V]\mathrm{MeV}^{d/2}"
/>

i.e.

<img
  src="https://latex.codecogs.com/svg.latex?\mathrm{MeV}=\mathrm{MeV}+[V]"
/>

hence <img
  src="https://latex.codecogs.com/svg.latex?[V]=MeV"
/>.

### Reference scale

We introduce the dimensionful scale <img
  src="https://latex.codecogs.com/svg.latex?m_e=0.5\frac{\mathrm{MeV}}{c^2}"
/> ("electron mass") to make everything dimensionless in the calculations: noting that

<img
  src="https://latex.codecogs.com/svg.latex?\frac{1}{m_e}=2\frac{c^2}{\mathrm{MeV}}=400\frac{c}{\hbar}\mathrm{fm}=1.33\cdot{10}^{-6}\frac{c^2}{\hbar}\mathrm{fs}"
/>,

one translates physical lengths L (and their increments &Delta;L) to

<img
  src="https://latex.codecogs.com/svg.latex?\lambda=L\frac{m_ec^2}{\hbar{c}}"
/>,

times t to

<img
  src="https://latex.codecogs.com/svg.latex?\tau=tc\frac{m_ec^2}{\hbar{c}}"
/>,

masses m to

<img
  src="https://latex.codecogs.com/svg.latex?\mu=\frac{m}{m_e}"
/>,

potentials V to

<img
  src="https://latex.codecogs.com/svg.latex?v=\frac{V}{m_ec^2}"
/>,

wave numbers k to

<img
  src="https://latex.codecogs.com/svg.latex?h=\frac{k}{m_ec/\hbar}"
/>

and the wave function &Psi; to

<img
  src="https://latex.codecogs.com/svg.latex?\phi=\frac{\Psi}{\left(\frac{m_ec}{\hbar}\right)^{d/2}}"
/>.

## Dimensionless Schroedinger equation

Under the change to dimensionless variables,

<img
  src="https://latex.codecogs.com/svg.latex?i\hbar\frac{\mathrm{d}\Psi}{\mathrm{d}t}=-\frac{\hbar^2}{2m}\frac{\mathrm{d}^2\Psi}{\mathrm{d}x^2}+V\Psi"
/>

becomes then

<img
  src="https://latex.codecogs.com/svg.latex?i\frac{\Delta\phi}{\Delta\tau}=-\frac{1}{2\mu}\frac{\Delta^2\phi}{\Delta\lambda^2}+v\phi"
/>

i.e.

<img
  src="https://latex.codecogs.com/svg.latex?\Delta\phi=-i\Delta{\tau}\left[-\frac{1}{2\mu}\frac{\Delta^2\phi}{\Delta\lambda^2}+v\phi\right]"
/>

## Frequencies, imposing periodicity

We enforce the requirement that each frequency inserted into the initial
wave function be a multiple of a fundamental one: this prevents, in case
of periodic boundary conditions, the occurrence of discontinuities.

Physically, we require that e<sup>ikL</sup>=1, which implies

<img
  src="https://latex.codecogs.com/svg.latex?h\lambda=2\pi{m}h_0~,~h_0=\frac{2\pi}{\lambda}"
/>.

The fact that any mode must have a wave number that is a multiple of the above
h<sub>0</sub> is enforced in the code (by approximating any naively set value).

## Energy of the system

With the caveat that the value of the potential at its minimum is arbitrary
(we customarily set it to zero, however), we calculate the energy as

<img
  src="https://latex.codecogs.com/svg.latex?E=\langle\Psi|E|\Psi\rangle"
/>

which in dimensionless units leads to

<img
  src="https://latex.codecogs.com/svg.latex?E=m_ec^2\cdot{e}"
/>,

where

<img
  src="https://latex.codecogs.com/svg.latex?e=\Delta\lambda\sum_i\phi^\star_i\left(-\frac{1}{2\mu}\frac{\Delta^2}{\Delta\lambda^2}+v\right)\phi_i"
/>

## Boundary conditions

Periodic and fixed can be chosen; with periodic b.c. one has a little more control over divergencies
and spurious high-frequency modes that may arise; however, a proper tuning of the relationship between
time and space integration intervals keeps them under control when using the Runge-Kutta scheme
described below. In any case the whole-frequency enforcing is performed regardless of the boundary conditions.

## Fourth-order Runge-Kutta integration scheme

The explicit implementation that is used in this code is as follows:
calling F the discrete evolution operator, as in

<img
  src="https://latex.codecogs.com/svg.latex?\frac{\Delta\phi(\lambda,\tau)}{\Delta\tau}=F[\phi]"
/>,

the following spatial functions are calculated:

<img
  src="https://latex.codecogs.com/svg.latex?k_1=F[\phi]"
/>

<img
  src="https://latex.codecogs.com/svg.latex?k_2=F[\phi+\frac{\Delta\tau}{2}k_1]"
/>

<img
  src="https://latex.codecogs.com/svg.latex?k_3=F[\phi+\frac{\Delta\tau}{2}k_2]"
/>

<img
  src="https://latex.codecogs.com/svg.latex?k_4=F[\phi+\Delta\tau{k_3}]"
/>

so that for the next update step the wave function has been incremented by

<img
  src="https://latex.codecogs.com/svg.latex?\Delta\phi=\frac{\Delta\tau}{6}\left[k_1+2k_2+2k_3+k_4\right]"
/>

### Matricial form of the RK scheme

The Runge-Kutta approach above is linear in the wave function, so it can be
recast in terms of the action of a matrix H acting on &phi; to produce the
wavefunction for the next timestep.

Moreover, if &phi; becomes 1+&Delta;&phi; in each single timestep, then
one can perform N updates as one matrix operation after building

<img
  src="https://latex.codecogs.com/svg.latex?U=(1+H)^N"
/>,

so that the (N-fold) update reads &phi; &#x2192; U&phi;. In turn, calling
&Delta;&tau; the "small" timestep, H is built as

<img
  src="https://latex.codecogs.com/svg.latex?H=(\mathcal{F}+\frac{\mathcal{F}^2}{2}+\frac{\mathcal{F}^3}{6}+\frac{\mathcal{F}^4}{24})"
/>,

where
<img
  src="https://latex.codecogs.com/svg.latex?\mathcal{F}=\Delta\tau\cdot{F}"
/>.

_Note_: In cases where the potential is a function of time, however, all of this pre-processing is
not very useful, probably, since most of the computation will need to be performed at each
change of the potential (i.e. possibly at each draw operation or even time step).
