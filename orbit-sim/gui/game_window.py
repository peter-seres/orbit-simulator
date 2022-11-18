import arcade
import arcade.gui
import pyglet
import numpy as np
from typing import Tuple
from pyglet.math import Vec2
from settings import AppSettings, Color
from functools import wraps


def shift_mouse_position(func):
    """ Decorator to convert the x, y coordinate arguments to screen space coordinates"""

    @wraps(func)
    def wrapper(*args):
        obj: GameWindow = args[0]
        x: int = args[1]
        y: int = args[2]
        rest = args[3:]
        x, y = obj.window2screen(x, y)
        return func(obj, x, y, *rest)

    return wrapper


class GameWindow(arcade.Window):
    """ Implement an arcade game window using the App Settings
        Adds basic key bindings to resize and close the app.
        Adds camera panning movement and gui draw calls.
    """

    def __init__(self):
        super().__init__(
            AppSettings.WIDTH_INIT,
            AppSettings.HEIGHT_INIT,
            AppSettings.TITLE,
            AppSettings.FULLSCREEN,
            AppSettings.RESIZABLE,
            gl_version=(4, 3)
        )
        arcade.set_background_color(Color.BACKGROUND_COLOR)

        # Set custom icon
        self.set_icon(
            pyglet.image.load(AppSettings.ICON_16),
            pyglet.image.load(AppSettings.ICON_32),
        )

        # Make two cameras
        self.main_camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # GUI Elements
        self.gui_elements = arcade.SpriteList()

        # Recenter camera
        self.center_viewport_on(0, 0, speed=1.0)

    def set_mouse_platform_visible(self, platform_visible: bool = None):
        """Mandatory implementation of base abstract class. Makes mouse visible over window."""
        super().set_mouse_platform_visible(platform_visible)

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
                self.center_viewport_on(0, 0)

    def on_draw(self):
        """ Draw GUI elements. Should be called after everything else"""
        if AppSettings.SHOW_GUI:
            self.gui_camera.use()
            self.gui_elements.draw()

    def shift_viewport(self, dx, dy):
        """ Panning across the screen space. """
        
        # Current camera position
        x, y = self.main_camera.position

        # Set new camera position:
        self.main_camera.move(Vec2(x - 2 * dx, y - 2 * dy))

    def center_viewport_on(self, x: int = 0, y: int = 0, speed: float = 0.3):
        """ Put the screen space origin in the middle of the window"""

        x -= self.main_camera.viewport_width / 2
        y -= self.main_camera.viewport_height / 2
        self.main_camera.move_to(Vec2(x, y), speed=speed)

    def window2screen(self, x, y):
        """ Convert window space coordinate to screen space. (game space) """
        dx, dy = self.main_camera.position
        return x + dx, y + dy

    def screen2window(self, x, y) -> Tuple[int, int]:
        """ Convert window space coordinate to screen space. (game space) """
        dx, dy = self.main_camera.position
        return x - dx, y - dy

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        """ Panning functionality. """
        if buttons == 4:
            self.shift_viewport(dx, dy)

    def on_resize(self, width: float, height: float):
        self.main_camera.resize(int(width), int(height))
        self.gui_camera.resize(int(width), int(height))
