import array
from typing import Optional, Tuple
import arcade.gl
import numpy as np
import random
from utils import normalize, rotate_vector_2D
from dataclasses import dataclass
from orbit_simulation.celestial_body import CelestialBody
from settings import VFXSettings as VFX
from settings import OrbitSettings


@dataclass
class Burst:
    ssbo_1: arcade.gl.Buffer
    ssbo_2: arcade.gl.Buffer
    vao_1: arcade.gl.Geometry
    vao_2: arcade.gl.Geometry


class ParticleBurstHandler:
    def __init__(self, ctx: arcade.ArcadeContext):
        # Store the context
        self.ctx = ctx

        # Enable alpha blending
        self.ctx.enable(self.ctx.BLEND)

        # Storage for Burst objects
        self.bursts: list[Burst] = []

        # Particle settings
        self.particle_count = VFX.PARTICLE_COUNT

        # Group layout for compute shader
        self.group_x, self.group_y = VFX.COMPUTE_SHADER_GROUP_COUNTS

        # Compile shaders
        self.compute_shader, self.program = self.compile_shaders()

        print("Successfully compiled shaders")

    def get_nr_particles(self) -> int:
        return len(self.bursts) * self.particle_count

    def set_uniforms(self, dt: float, bodies: list[CelestialBody]):
        self.compute_shader["dt"] = dt

        x = []
        for idx in range(10):
            try:
                body = bodies[idx]
                pos = body.position
                GM = body.mass * OrbitSettings.G
            except IndexError:
                pos = (1_000_000_000.0, 1_000_000_000)
                GM = 0.00000001

            x.append(pos[0])
            x.append(pos[1])
            x.append(GM)

        self.compute_shader["planets"] = x

    def compile_shaders(self) -> Tuple[arcade.gl.Program, arcade.gl.Program]:
        # Compile shaders

        with open(VFX.COMPUTE_SHADER) as file:
            compute_shader_source = file.read()

        with open(VFX.VERTEX_SHADER) as file:
            vertex_shader_source = file.read()

        with open(VFX.FRAGMENT_SHADER) as file:
            fragment_shader_source = file.read()

        # Create our compute shader.
        # Search/replace to set up our compute groups
        compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_X",
                                                              str(self.group_x))
        compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_Y",
                                                              str(self.group_y))
        compute_shader = self.ctx.compute_shader(source=compute_shader_source)

        # Program for visualizing the balls
        program = self.ctx.program(
            vertex_shader=vertex_shader_source,
            fragment_shader=fragment_shader_source,
        )

        return compute_shader, program

    def generate_particles(self, pos, vel, col):
        print(f"Generating {self.particle_count} particles at position: {pos} with mean velocity {vel}")

        # Color is in [0, 1] space
        col = np.array(col) / 255.0

        # Get the direction and magnitude of the velocity:
        direction, speed = normalize(vel)

        for _ in range(self.particle_count):

            # Add random gaussian angle and speed deviation to the velocity
            angle_deviation = random.gauss(0, VFX.PARTICLE_SPREAD_ANGLE)
            speed_deviation = random.gauss(0.0, VFX.PARTICLE_SPREAD_SPEED)

            # Make sure the noise doesn't make it go backwards:
            speed += speed_deviation
            if speed < 0:
                speed = 0.0

            # add the angle deviation to the final vector:
            vel = rotate_vector_2D(v=direction * speed, angle=angle_deviation)

            # Padding for std430 buffer layout:
            pos = (pos[0], pos[1], 0.0, 0.0)
            vel = (vel[0], vel[1], 0.0, 0.0)
            col = (col[0], col[1], col[2], 1.0)

            # Yeild a single element at once for the buffer
            for f in (*pos, *vel, *col):
                yield f

    def create_planet_data_buffer(self, bodies: list[CelestialBody]) -> arcade.gl.Buffer:

        def generate_data_points():

            for body in bodies:
                pos = body.position
                body_GM = body.mass * OrbitSettings.G
                for f in (pos[0], pos[1], 0.0, body_GM):
                    yield f

        initial_data = generate_data_points()
        ssbo = self.ctx.buffer(data=array.array("f", initial_data))
        return ssbo

    def create_burst(self, pos, vel, col):

        # Get initial particle data
        initial_data = self.generate_particles(pos, vel, col)

        # Create two buffers for compute shader
        ssbo_1 = self.ctx.buffer(data=array.array("f", initial_data))
        ssbo_2 = self.ctx.buffer(reserve=ssbo_1.size)

        # Buffer format (position, velocity, color) with std430 layout:
        buffer_format = "4f 4x4 4f"

        # Vertex shader inputs:
        attributes = ["in_pos", "in_col"]

        # Vertex attribute objects:
        vao_1 = self.ctx.geometry(
            [arcade.gl.BufferDescription(
                ssbo_1,
                buffer_format,
                attributes,
            )],
            mode=self.ctx.POINTS
        )

        vao_2 = self.ctx.geometry(
            [arcade.gl.BufferDescription(
                ssbo_2,
                buffer_format,
                attributes,
            )],
            mode=self.ctx.POINTS
        )

        # Create the Burst object and add it to the list of bursts
        burst = Burst(ssbo_1, ssbo_2, vao_1, vao_2)
        self.bursts.append(burst)
        print(f"ParticleBurst created with {self.particle_count} particles.")

    def draw_burst(self, burst: Burst, paused: bool):
        # Bind buffers
        burst.ssbo_1.bind_to_storage_buffer(binding=0)
        burst.ssbo_2.bind_to_storage_buffer(binding=1)

        # Run compute shader
        if not paused:
            self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)

        # Draw the points
        burst.vao_2.render(self.program)

        if not paused:
            # Swap the buffers
            burst.ssbo_1, burst.ssbo_2 = burst.ssbo_2, burst.ssbo_1

            # Swap the geometry
            burst.vao_1, burst.vao_2 = burst.vao_2, burst.vao_1

    def draw(self, paused: bool):
        for b in self.bursts:
            self.draw_burst(b, paused)

    def clear_all(self):
        self.bursts = []
