import arcade
import arcade.color as color
from utils import Vector
from typing import Callable
from orbit_simulation.celestial_body import CelestialBody
import itertools
from copy import deepcopy
from settings import OrbitSettings, Color


class OrbitSimulator:
    """Keeps track of the celestial bodies and simulates their movement."""

    def __init__(self, destr_callback: Callable):
        self.bodies = [CelestialBody.make_sun(), CelestialBody.make_earth()]

        # Destruction event function
        self.destruction_callback = destr_callback

        # Prediction bodies
        self.virtual_bodies = []

    def get_sun(self):
        return self.bodies[0]

    def physics_step(self, dt, bodies, n_body_sim: bool = True):
        if n_body_sim:
            # Dynamics: Calculate gravitational accelerations for each pair of the bodies
            for (a, b) in itertools.combinations(bodies, 2):

                # Relative position
                F = CelestialBody.gravitational_force(a, b)

                # Update velocities using the acceleration
                a.velocity += F / a.mass * dt
                b.velocity += -F / b.mass * dt
        else:
            # Dynamics: Calculate the graviational aceleration for each body:
            for b in bodies[1:]:
                F = CelestialBody.gravitational_force(b, self.get_sun())
                b.velocity += F / b.mass * dt

        for idx, body in enumerate(bodies):
            # Save position to object's position history
            body.history.append(tuple(body.position))

            # Update position
            body.position += body.velocity * dt

    def destruction_check(self, screen_size: Vector):
        for idx, body in enumerate(self.bodies):

            # Delete objects that are too far away
            if body.is_too_far_away(screen_size):
                print(f"Deleting body too far away at position: {body.position}.")
                del self.bodies[idx]

            # Delete objects that fly too close to the sun
            if body.is_too_close_to_sun(self.get_sun()):
                print(f"Deleting body too close to Sun.")
                self.destruction_callback(body.position, body.velocity, body.color)
                del self.bodies[idx]

    def step(self, dt: float, screen_size: Vector):
        self.physics_step(
            dt, self.bodies, n_body_sim=OrbitSettings.N_BODY_SIM
        )
        self.destruction_check(screen_size)

    def predict(self, position: Vector, velocity: Vector):
        """Predict the future if a new planet with state appered."""

        newBody = CelestialBody(position, velocity, color=color.CYAN)
        self.virtual_bodies = deepcopy(self.bodies)
        self.virtual_bodies.append(newBody)

        for b in self.virtual_bodies:
            b.virtual = True

        for i in range(OrbitSettings.FUTURE_LENGTH):
            self.physics_step(
                OrbitSettings.PREDICTION_DT,
                self.virtual_bodies,
                n_body_sim=OrbitSettings.N_BODY_PRED,
            )

    def clear_histories(self):
        """Clear the history of each planet due to screen size change."""
        [body.clear_history() for body in self.bodies]

    def clear_futures(self):
        self.virtual_bodies = []

    def draw_bodies(self):
        """Draw a filled circle onto the screen for each celestial body."""
        for body in self.bodies:
            screen_position = body.position
            arcade.draw_circle_filled(
                *screen_position, radius=body.size, color=body.color
            )

    def draw_histories(self):
        for body in self.bodies:
            if body.history:
                arcade.draw_points(body.history, color=Color.HISTORY_COLOR)

    def draw_futures(self):
        for body in self.virtual_bodies:
            if body.history:
                arcade.draw_points(body.history, color=Color.PREDICTION_COLOR)

    def delete_latest_body(self):
        b = self.bodies[-1]
        if b is not self.get_sun():
            print("CTRL + D: Deleting last celestial body")
            self.destruction_callback(b.position, b.velocity, b.color)
            self.bodies[-1].clear_history()
            del self.bodies[-1]

    def add_body(self, *args, **kwargs):
        newCelestialBody = CelestialBody(*args, **kwargs)
        self.bodies.append(newCelestialBody)
