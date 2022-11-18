#version 430

// Set up our compute groups
layout(local_size_x=COMPUTE_SIZE_X, local_size_y=COMPUTE_SIZE_Y) in;

// Uniforms:
uniform float dt;
uniform vec3 planets[10];

// Structure of the ball data
struct Body
{
    vec4 pos;
    vec4 vel;
    vec4 color;
};

// Input buffer
layout(std430, binding=0) buffer bodies_in
{
    Body bodies[];
} In;

// Output buffer
layout(std430, binding=1) buffer bodies_out
{
    Body bodies[];
} Out;

void main()
{
    // Get the index of the current body
    int index = int(gl_GlobalInvocationID);

    // Current body
    Body current_body = In.bodies[index];

    // Fetch position, velocity and color;
    vec4 p = current_body.pos.xyzw;
    vec4 v = current_body.vel.xyzw;
    vec4 c = current_body.color.xyzw;

    for(int i = 0; i < 10; ++i)
    {
        vec3 current_planet = planets[i];

        vec2 body_pos = current_planet.xy;
        float body_gm = current_planet.z;

        // Vector pointing from ball to the Sun
        vec2 R = normalize(body_pos - p.xy);

        // Distance
        float R_norm = distance(p.xy, body_pos);

        // Newton's law
        vec2 acc = R * body_gm / (R_norm * R_norm);

        // Update velocity
        v.xy += acc * dt;
    }

    // Update position
    p.xy += v.xy * dt;

    // Create output ball
    Body output_body;

    // Assign updated variables
    output_body.pos.xyzw = p.xyzw;
    output_body.vel.xyzw = v.xyzw;
    output_body.color.xyzw = c.xyzw;

    // Write to output buffer
    Out.bodies[index] = output_body;
}
