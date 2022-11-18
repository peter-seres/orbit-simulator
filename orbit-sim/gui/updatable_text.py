import time
import arcade
from collections import deque
from vfx.particle_bursts import ParticleBurstHandler
from orbit_simulation import OrbitSimulator


class UpdatableText:
    def __init__(self, x, y, fix_text: str, font_size: int = 11, color=arcade.color.WHITE):
        self.fix_text = fix_text
        self.text = arcade.Text(fix_text, x, y, color, font_size)

    def update_text(self, value):
        self.text.value = f"{self.fix_text}: {value}"

    def draw(self):
        self.text.draw()


class PlanetCounter(UpdatableText):
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, fix_text="Nr of objects", **kwargs)

    def update_and_draw(self, orbit_simulator: OrbitSimulator):
        self.update_text(value=len(orbit_simulator.bodies))
        super().draw()
        

class ParticleCounter(UpdatableText):
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, fix_text="Nr of particles", **kwargs)

    def update_and_draw(self, particle_handler: ParticleBurstHandler):
        self.update_text(value=particle_handler.get_nr_particles())
        super().draw()


class FPSCounter(UpdatableText):
    def __init__(self, x, y, average_of: int = 30, **kwargs):
        super().__init__(x, y, fix_text="FPS", **kwargs)
        self.frame_times = deque(maxlen=average_of)
        self.fps: float = 0.0

    def update_and_draw(self):
        self.update_fps()
        super().update_text(value=f"{self.fps:0.1f}")
        super().draw()

    def update_fps(self):
        self.frame_times.append(time.time())
        if len(self.frame_times) > 1:
            self.fps = len(self.frame_times) / (self.frame_times[-1] - self.frame_times[0])
