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
  
  // luz difusa
  float specularStrength = 0.5;
  vec3 norm = normalize(normal);
  vec3 viewDir = normalize(viewPos - fPos);
  vec3 lightDir = normalize(lightPos - fPos);
  vec3 reflectDir = reflect(lightDir, norm);
  float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
  vec3 specular = specularStrength * spec * lightColor;
 
  vec3 result = (specular + ambient) * objectColor;
  fcolor = vec4(result, 1.0);
}
 
