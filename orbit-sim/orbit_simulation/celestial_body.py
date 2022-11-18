from __future__ import annotations
from typing import Optional
import numpy as np
from dataclasses import dataclass, field
from utils import Vector, normalize
from collections import deque
from settings import Color, OrbitSettings


def random_color():
    return tuple(np.random.randint(70, 255, size=3))


@dataclass
class CelestialBody:
    """Object in space: described by position and velocity.
    Each object maintains a history of positions in screen and world coordinates.
    """

    position: np.ndarray = field(default=np.zeros(2, dtype=np.float64))
    velocity: np.ndarray = field(default=np.zeros(2, dtype=np.float64))
    mass: float = 1.0
    size: float = 5.0
    color: Optional[tuple] = field(default_factory=random_color, repr=False)
    history: deque[tuple[float, float]] = field(
        default=deque(maxlen=OrbitSettings.HISTORY_LENGTH), repr=False
    )
    __virtual: bool = False

    def __post_init__(self):
        self.position = np.array(self.position, dtype=np.float64)
        self.velocity = np.array(self.velocity, dtype=np.float64)

    @property
    def virtual(self) -> bool:
        return self.virtual

    @virtual.setter
    def virtual(self, value: bool):
        """Virtual bodies are used to predict the future. The history of the virtual body can."""
        self.__virtual = value
        self.history = deque(maxlen=OrbitSettings.FUTURE_LENGTH)

    @staticmethod
    def gravitational_force(a: CelestialBody, b: CelestialBody) -> np.ndarray:
        # Relative position
        direction, distance = normalize(b.position - a.position)

        # Newton's law
        return direction * (OrbitSettings.G * a.mass * b.mass / distance**2)

    def is_too_far_away(self, screen_size: Vector) -> bool:
        """Check whether the body is far away from the viewport."""
        return (abs(self.position) > 2 * screen_size).all()

    def is_too_close_to_sun(self, sun: CelestialBody) -> bool:
        """Check whether the body is close to the Sun object."""
        if self is sun:
            return False

        _, dist = normalize(self.position - sun.position)
        return dist < sun.size + self.size + OrbitSettings.SUN_DESTRUCTION_RANGE

    def clear_history(self) -> None:
        self.history.clear()

    @staticmethod
    def make_sun() -> CelestialBody:
        return CelestialBody(
            mass=OrbitSettings.SUN_MASS,
            color=Color.SUN_COLOR,
            size=OrbitSettings.SUN_SIZE,
        )

    @staticmethod
    def make_earth() -> CelestialBody:
        return CelestialBody(
            position=OrbitSettings.EARTH_POSITION,
            velocity=OrbitSettings.EARTH_VELOCITY,
            color=Color.EARTH_COLOR,
        )
