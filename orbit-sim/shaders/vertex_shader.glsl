#version 430
//
// Use arcade's global projection UBO
uniform Projection {
    mat4 matrix;
} proj;

// Input
in vec4 in_pos;
in vec4 in_col;

// Output
out vec4 vertex_color;

void main()
{
    // Project from screen space to openGL space
    gl_Position = proj.matrix * vec4(in_pos.xy, 0.0, 1.0);

    // Assign vertex color
    vertex_color = in_col;
}
