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


  // luz ambiente
  if(reflecc[0] == 1.0){
    float ambientStrength = 0.1;
    ambient = ambientStrength * lightColor;
  }else{
    ambient = vec3(0,0,0);
  }
  // luz difusa
  if(reflecc[1] == 1.0){
    float difuseStregth = 1.0;
    norm = normalize(normal);
    lightDir = normalize(lightPos-fPos);
    float diff = max(dot(norm,lightDir),0.0);
    difuse = diff * lightColor * difuseStregth;
  }else{
    difuse = vec3(0,0,0);
  }
  // luz especular
  if(reflecc[2] == 1.0){
    float specularStregth = 0.5;
    vec3 viewDir = (viewPos - fPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    specular = specularStregth * spec * lightColor;
  }else{
    specular = vec3(0,0,0);
  }
  vec3 result = (ambient + difuse + specular) * objectColor;
  fcolor = vec4(result, 1.0);
}

