# Orbit Simulator Game

N-body gravity simulation to play with planet orbits, written in `python` using the `arcade` API.

Features:

- LMB: Drag and drop new planets into the simulation.
- MMB: Drag and drop particles into the simulation.
- D: Destroy the planets into particles.
- C: Destroy all particles.

![showcase1](https://github.com/peter-seres/orbit-simulator/blob/master/showcase/screenshot_1.png)

![showcase2](https://github.com/peter-seres/orbit-simulator/blob/master/showcase/screenshot_2.png)

## Install and Run

### Using conda
`conda env create --file environment.yml`
`conda activate orbit-sim`

### Using pip
`pip install numpy arcade pyglet`

### Run the game

CD into the repository and run
`python orbit-sim`

## Implementation to-do list
  - Custom gui elements:
    - slider
    - button
    - fps counter
    - planet counter
  - Lifetime & destruction of particles
    - set the particle mass to zero 
  - Fix history color bug
  - Slider for mass of planet
  - Save / load the situationa into a file
  - Main Menu
