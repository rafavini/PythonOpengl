#version 130
uniform vec3 objectColor;
uniform vec3 lightColor;
uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 reflecc;

in vec3 normal;
in vec3 fPos;

out vec4 fcolor;

void main(){
  vec3 ambient;
  vec3 specular; 
  vec3 difuse;
  vec3 norm;
  vec3 lightDir;
  vec3 result;


  // luz ambiente
  if(reflecc[0] == 1.0){
    float ambientStrength = 0.1;
    ambient = ambientStrength * lightColor;
  }else{
    ambient = vec3(0,0,0);
  }
  norm = normalize(normal);
  lightDir = normalize(lightPos-fPos);
  // luz difusa
  if(reflecc[1] == 1.0){
    float difuseStregth = 1.0;
    float diff = max(dot(norm,lightDir),0.0);
    difuse = diff * lightColor * difuseStregth;
  }else{
    difuse = vec3(0,0,0);
  }
  // luz especular
  if(reflecc[2] == 1.0){
    float specularStrength = 0.5;
    norm = normalize(normal);
    vec3 viewDir = normalize(viewPos - fPos);
    lightDir = normalize(lightPos - fPos);
    vec3 reflectDir = reflect(lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    specular = specularStrength * spec * lightColor;
  }else{
    specular = vec3(0,0,0);
  }
  
  if(reflecc[2] == 1.0){
    ambient = 0.1 * lightColor;
    result = (specular + ambient) * objectColor;
  }else{
    result = (ambient + difuse) * objectColor;
  }
  
  fcolor = vec4(result, 1.0);
}

