from functools import wraps
import arcade
import arcade.color as color
from pyglet.math import Vec2
import numpy as np


def shift_mouse_position(func):
    @wraps(func)
    def wrapper(*args):
        obj: CamerasWindow = args[0]
        x: int = args[1]
        y: int = args[2]
        rest = args[3:]
        x, y = obj.window2screen(x, y)
        return func(obj, x, y, *rest)

    return wrapper


class CamerasWindow(arcade.Window):
    """Implement an arcade game window using the App Settings"""

    def __init__(self):
        super().__init__(800, 600, "GUI Experiment", fullscreen=False, resizable=True, gl_version=(4, 3))
        arcade.set_background_color(color.BLACK)

        # Make two cameras
        self.main_camera = arcade.Camera(self.width, self.height)
        self.main_camera.use()
        self.gui_camera = arcade.Camera(self.width, self.height)

        # GUI Elements
        self.gui_elements = arcade.SpriteList()
        self.gui_elements.append(
            arcade.create_text_sprite(
                text="Test UI element",
                start_x=50,
                start_y=100,
                color=arcade.color.WHITE,
            )
        )

    @property
    def screen_size(self):
        return np.array([self.width, self.height])

    def on_key_release(self, symbol: int, modifiers: int):
        """Handle window logic keybinds"""

        match (symbol, modifiers):
            case (arcade.key.ESCAPE | arcade.key.Q, _):
                self.close()

            case (arcade.key.F | arcade.key.ENTER, _):
                self.set_fullscreen(not self.fullscreen)

            case (arcade.key.SPACE, _):
                self.center_viewport_on()

    def shift_viewport(self, dx, dy):
        """ Panning across the screen space. """
        # Current camera position
        x, y = self.main_camera.position

        # Set new camera position:
        self.main_camera.move(Vec2(x - 2 * dx, y - 2 * dy))

    def center_viewport_on(self, x=0, y=0):
        """ Put the screen space origin in the middle of the window"""

        x -= self.main_camera.viewport_width / 2
        y -= self.main_camera.viewport_height / 2
        self.main_camera.move_to(Vec2(x, y), speed=0.4)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        """ Panning functionality. """
        if buttons == 4:
            print(f"Dragging mouse {dx, dy}")
            self.shift_viewport(dx, dy)

    def set_mouse_platform_visible(self, platform_visible: bool = None):
        """Mandatory implementation of base abstract class. Makes mouse visible over window."""
        super().set_mouse_platform_visible(platform_visible)

    def on_resize(self, width: float, height: float):
        self.main_camera.resize(int(width), int(height))
        self.gui_camera.resize(int(width), int(height))

    def window2screen(self, x, y):
        """ Convert window space coordinate to screen space. (game space) """
        dx, dy = self.main_camera.position
        return x + dx, y + dy

    def screen2window(self, x, y) -> (int, int):
        """ Convert window space coordinate to screen space. (game space) """
        dx, dy = self.main_camera.position
        return x - dx, y - dy


class Game(CamerasWindow):
    def __init__(self):
        super().__init__()
        self.viewport_shift = np.zeros(2)

        self.sprites = arcade.SpriteList()
        self.shapes = arcade.ShapeElementList()

        # Add coordinate system
        self.shapes.append(arcade.create_line(-10000.0, 0.0, 10000.0, 0.0, color=(120, 120, 120)))
        self.shapes.append(arcade.create_line(0.0, -10000.0, 0.0, 10000.0, color=(120, 120, 120)))

    def on_key_release(self, symbol: int, modifiers: int):
        super().on_key_release(symbol, modifiers)

    def on_draw(self):
        # Set  maincamera
        self.main_camera.use()

        # Clear screen
        self.clear()

        # Game draw calls
        self.shapes.draw()

        # GUI draw calls
        self.gui_camera.use()
        self.gui_elements.draw()

    def add_point(self, x, y):
        self.shapes.append(
            arcade.create_ellipse_filled(x, y, width=3, height=3, color=(255, 255, 255))
        )

    @shift_mouse_position
    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        if button == 1:
            self.add_point(x, y)


if __name__ == '__main__':
    Game()
    arcade.run()
