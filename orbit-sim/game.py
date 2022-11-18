import arcade
import numpy as np
from gui import generate_instructions, FPSCounter, PlanetCounter, ParticleCounter
from utils import Vector, normalize
from orbit_simulation import OrbitSimulator
from typing import Optional, Tuple
from settings import AppSettings, Color, OrbitSettings
from gui.game_window import GameWindow, shift_mouse_position
from vfx import ParticleBurstHandler


class OrbitSimulatorWindow(GameWindow):
    """Handles the Game Logic, UX and game object draw calls"""

    def __init__(self):
        super().__init__()

        # Simulator instance
        self.orbit_simulator = OrbitSimulator(destr_callback=self.on_planet_destruction)

        # Particle bursts
        self.particles = ParticleBurstHandler(ctx=self.ctx)

        # Store mouse status information for "drag and drop"
        self.mousePress: Optional[Vector] = None
        self.latestMousePosition: Optional[Vector] = None
        self.paused = False

        # Mass creation setting:
        self.massToPlace = 1_0
        self.n_particles = 0

        # GUI elements:
        for instruction in generate_instructions(*AppSettings.INSTRUCTIONS_LOCATION, y_sep=AppSettings.INSTRUCTIONS_Y_SEP):
            self.gui_elements.append(instruction)

        self.fps = FPSCounter(*AppSettings.FPS_LOCATION)
        self.planet_counter = PlanetCounter(*AppSettings.PLANET_COUNT_LOCATION)
        self.particle_counter = ParticleCounter(*AppSettings.PARTICLE_COUNT_LOCATION)

    def on_planet_destruction(self, pos, vel, col):
        """Callback when a planet is destroyed."""
        self.particles.create_burst(pos, vel, col)
        self.n_particles += 1

    def on_resize(self, *args, **kwargs):
        super().on_resize(*args, **kwargs)
        self.orbit_simulator.clear_histories()

    def on_update(self, delta_time: float):
        """This method runs the physics and motion of each body."""

        if self.paused:
            return

        self.orbit_simulator.step(dt=delta_time, screen_size=self.screen_size)

    def draw_drag_ang_shoot_line(self):
        # Draw UI line when dragging
        if self.mousePress is not None and self.latestMousePosition is not None:
            arcade.draw_line(
                *self.mousePress, *self.latestMousePosition, Color.DRAG_COLOR
            )

    def on_draw(self):
        # Set main camera for game space drawing
        self.main_camera.use()

        # Clear screen
        self.clear()

        # Draw histories:
        self.orbit_simulator.draw_histories()

        # Draw futures:
        if self.paused:
            self.orbit_simulator.draw_futures()

        # Draw particles:
        self.particles.set_uniforms(dt=1/60.0, bodies=self.orbit_simulator.bodies)
        self.particles.draw(self.paused)

        # Draw Bodies:
        self.orbit_simulator.draw_bodies()

        # Draw line when dragging
        self.draw_drag_ang_shoot_line()

        # GUI widgets are drawn by the base class:
        super().on_draw()

        self.fps.update_and_draw()
        self.planet_counter.update_and_draw(orbit_simulator=self.orbit_simulator)
        self.particle_counter.update_and_draw(self.particles)

    def on_key_release(self, symbol: int, modifiers: int):
        """Handle game logic keybinds"""
        super().on_key_release(symbol, modifiers)

        match (symbol, modifiers):
            case (arcade.key.P, _):
                self.paused = not self.paused
                print("P: Game paused") if self.paused else print("P: Game unpaused")

            case (arcade.key.D, _):
                print("D: destroying last planet")
                self.orbit_simulator.delete_latest_body()

            case (arcade.key.C, _):
                print("C: clearing all particles")
                self.particles.clear_all()

            case (arcade.key.UP, _):
                self.massToPlace += 50.0
                print(f"Mass increased: {self.massToPlace:.2f}")

            case (arcade.key.DOWN, _):
                self.massToPlace = max(1.0, self.massToPlace - 50.0)
                print(f"Mass decreased: {self.massToPlace:.2f}")


    def get_drag_release_info(self, mousePress: Optional[Vector], mouseRelease: Vector) -> Optional[Tuple[Vector, Vector]]:
        """ Handle the final release of a drag and drop: compare the two mouse locations."""

        if mousePress is None:
            return
        
        # Type handling
        mousePress = np.array(mousePress)
        mouseRelease = np.array(mouseRelease)
        
        # Drag and drop direction and distance:
        try:
            direction, distance = normalize(mousePress - mouseRelease, eps=1e-2)

        # Handle tiny mouse movements:
        except ZeroDivisionError:
            return

        if distance <= 5.0:
            return

        pos = self.mousePress
        vel = direction * distance * OrbitSettings.VEL_SCALAR

        return pos, vel

    @shift_mouse_position
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Called whenever a mouse button is pressed."""
        match (button, modifiers):
            
            # LMB Press
            case (1, _):
                self.mousePress = np.array([x, y])
                self.paused = True
            
            # MMB Press
            case (2, _):
                self.mousePress = np.array([x, y])
                self.paused = True

    @shift_mouse_position
    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """Called whenever a mouse button is released."""
        match (button, modifiers):
            
            # LMB Release
            case (1, _):
                if result := self.get_drag_release_info(mousePress=self.mousePress, mouseRelease=[x, y]):
                    # Reset
                    self.paused = False
                    self.mousePress = None
                    self.latestMousePosition = None

                    # Make a new planet
                    self.orbit_simulator.add_body(*result, mass=self.massToPlace)
                    self.orbit_simulator.clear_futures()
                    
            # MMB Release:
            case (2, _):
                if result := self.get_drag_release_info(mousePress=self.mousePress, mouseRelease=[x, y]):
                    
                    # Reset
                    self.paused = False
                    self.mousePress = None
                    self.latestMousePosition = None
                    
                    # Make a new planet
                    
                    pos, vel = result
                    col = arcade.color.ALMOND
                    
                    self.particles.create_burst(pos, vel, col)
                    self.orbit_simulator.clear_futures()
        
    @shift_mouse_position
    def on_mouse_drag(
        self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int
    ):
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)

        match (buttons, modifiers):
            
            # LMB or MMB drag
            case (1 | 2, _):
                
                # Update the mouse to the last position
                self.latestMousePosition = np.array([x, y])

                # Ignore fast movements
                if (
                    abs(dx) > AppSettings.DRAG_MOUSE_DELTA
                    or abs(dy) >= AppSettings.DRAG_MOUSE_DELTA
                ):
                    return

                # Dispatch a future prediction step
                if result := self.get_drag_release_info(mousePress=self.mousePress, mouseRelease=self.latestMousePosition):
                    self.orbit_simulator.predict(*result)
