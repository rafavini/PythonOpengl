#version 130
out vec4 color;

in vec3 lightingColor;

uniform vec3 vcolor;

void main(){
	color = vec4(lightingColor * vcolor, 1);
}
