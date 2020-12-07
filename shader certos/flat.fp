#version 130
out vec4 color;

flat in vec3 fcolor;

uniform vec3 vcolor;

void main(){
	color = vec4(fcolor * vcolor, 1);
}
