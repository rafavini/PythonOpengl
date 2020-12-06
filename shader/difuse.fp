#version 130
uniform vec3 objectColor;
uniform vec3 lightColor;
uniform vec3 lightPos;
uniform vec3 viewPos;

in vec3 normal;
in vec3 fPos;

out vec4 fcolor;

void main(){   
   
  // luz difusa
  float difuseStrength = 0.8;
  vec3 norm = normalize(normal);
  vec3 lightDir = normalize(lightPos - fPos);
  float diff = max(dot(norm,lightDir),0.0);
  vec3 diffuse = difuseStrength * diff * lightColor;
 
  vec3 result = diffuse * objectColor;
  fcolor = vec4(result, 1.0);
}
 
