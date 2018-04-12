# pyschroedinger

A playground to learn something about numerical integration of the Schroedinger equation

## Next steps

Consistency with use of physical units: apart from discretisation settings (number
of space steps and so on), everything else must be well-defined "in the continuum limit".


## Schroedinger equation

Here we go:

<img
  src="https://latex.codecogs.com/svg.latex?i\hbar\frac{\mathrm{d}\psi}{\mathrm{d}t}=(\frac{p^2}{2m}+V)\psi"
/>

Momentum operator (1-D):

<img
  src="https://latex.codecogs.com/svg.latex?p=-i\hbar\frac{\mathrm{d}}{\mathrm{d}x}\Rightarrow%20p^2=-\hbar^2\frac{\mathrm{d}^2}{\mathrm{d}x^2}"
/>

## Boundary conditions

At the moment we stick to periodic to avoid most discontinuity issues.
But even in this case, when using wave numbers to define plane waves
or wave packets, we enforce continuity with the requirement that

<img
  src="https://latex.codecogs.com/svg.latex?e^{k}=1\Rightarrow%20k=n\cdot\pi,n\in{N}"
/>

The way this requirement is stated is is going to change as the
clean handling of physical units is implemented.
