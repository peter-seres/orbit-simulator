#version 330

// Color from the vertex shader
in vec4 vertex_color;

// Output
out vec4 out_color;

void main()
{
    out_color = vertex_color;
}
