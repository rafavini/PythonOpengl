#version 130
uniform vec3 objectColor;
uniform vec3 lightColor;
uniform vec3 lightPos;
uniform vec3 viewPos;

in vec3 normal;
in vec3 fPos;

out vec4 fcolor;

void main(){

  // luz ambiente
  float ambientStrength = 0.1;
  vec3 ambient = ambientStrength * lightColor;
  
  vec3 result = ambient * objectColor;
  fcolor = vec4(result, 1.0);
}
 
