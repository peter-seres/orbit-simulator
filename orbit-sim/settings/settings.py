from settings.immutable import Settings
import arcade.color as color
from pathlib import Path


ASSETS = Path.cwd() / "assets"
SHADERS = Path.cwd() / "orbit-sim" / "shaders"

class AppSettings(Settings):
    # Game Window
    WIDTH_INIT = 800
    HEIGHT_INIT = 600
    TITLE = "Orbit Simulator"
    FULLSCREEN = False
    RESIZABLE = True
    ICON_16 = ASSETS / "icon16.png"
    ICON_32 = ASSETS / "icon32.png"

    # GUI
    PLANET_COUNT_LOCATION = (20, 340)
    PARTICLE_COUNT_LOCATION = (20, 320)
    FPS_LOCATION = (20, 300)
    INSTRUCTIONS_LOCATION = (20, 250)
    INSTRUCTIONS_Y_SEP = 21 

    # UX
    DRAG_MOUSE_DELTA = 2

    # Instruction GUI
    INSTRUCTIONS = [
        "LMB: Drag & shoot planets",
        "MMB: Drag & shoot particles",
        "RMB: Pan",
        "Space: Recenter",
        "D: Destroy last planet",
        "C: Clear particles",
        "P: Pause",
        "F / ENTER: Toggle Fullscreen",
        "ESC / Q: Quit",
    ]

    SHOW_GUI = True


class VFXSettings(Settings):
    PARTICLE_COUNT = 5000

    PARTICLE_SPREAD_ANGLE = 0.06
    PARTICLE_SPREAD_SPEED = 1.8

    PARTICLE_MIN_FADE_TIME = 0.5
    PARTICLE_MAX_FADE_TIME = 1.5

    WORLD2OPENGL_SPEED_SCALAR = 0.75

    # Shaders
    COMPUTE_SHADER = SHADERS / "compute_shader.glsl"
    VERTEX_SHADER = SHADERS / "vertex_shader.glsl"
    FRAGMENT_SHADER = SHADERS / "fragment_shader.glsl"

    # Compute Shader
    COMPUTE_SHADER_GROUP_COUNTS = (256, 1)


class Color(Settings):
    # Window
    BACKGROUND_COLOR = (14, 14, 10)

    # UI
    DRAG_COLOR = color.DARK_YELLOW

    # Planets
    EARTH_COLOR = color.BABY_BLUE
    SUN_COLOR = color.CADMIUM_YELLOW
    
    # History
    HISTORY_COLOR = color.GRAY_BLUE

    # Prediction
    PREDICTION_COLOR = color.LIGHT_CYAN


class OrbitSettings(Settings):
    G = 1.5

    # Drag and shoot velocity
    VEL_SCALAR = 2.5

    # Sun Settings
    SUN_MASS = 1e7
    SUN_SIZE = 10
    SUN_DESTRUCTION_RANGE = 25

    # Earth settings
    EARTH_POSITION = [200, 0]
    EARTH_VELOCITY = [0, 280]

    # Simulator settings
    HISTORY_LENGTH = 700
    FUTURE_LENGTH = 700
    PREDICTION_DT = 1 / 15.0
    N_BODY_SIM = True
    N_BODY_PRED = False
