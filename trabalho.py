'''Alunos: Rafael Vinicius e Calebe lemos
   como compilar: python3 trabalho.py entrada.txt'''

import sys
import numpy as np
import math 
import pywavefront as obj
import pyrr 
from pyrr import matrix44, Vector3
import re
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from PIL import *
from PIL import Image


vao = None
vbo = None
shaderProgram = None
#variaveis de transformacoes
uMat = None       
projection = None 
view = None    
model = None   
idProj = None   
idView = None  
# variaveis lookat e camera   
poscam = [0,0,0] 
lookat = [0,0,-1] 
# variaveis dos reflections
ambient = 0
specular = 0
diffuse = 0
reflectionFlag = 0
reflec = None
ambientForce = None
diffuseForce = None
specularForce = None
#variaveis de on e off wireMode,lightMode e axis
lightMode = 0
wireMode = 0
axisFlag = 0
vet_axis = 0
#variaveis das luzes
idLight = None
idLightPos = None
idColor = None
idViewPos = None

def readObjFile(path):
	return obj.Wavefront(path)

def lendo_obj(nome):
	texto = nome+'.obj'
	aux = readObjFile(texto)
	aux.parse()
	for name, material in aux.materials.items():
		return material.vertices

# le os arquivos do shaders
def readShaderFile(filename):
	with open('shader/' + filename, 'r') as myfile:
		return myfile.read()

def init(obj,lista_obj):
	global shaderProgram
	global vao
	global vbo
	# variaveis das tranformacoes
	global projection
	global idProj
	global idView
	global model
	global view
	global uMat
	#camera e lookat
	global poscam
	global lookat
	# variaveis dos reflections 
	global ambient
	global diffuse
	global specular
	global reflectionFlag
	global reflec
	# variaveis da luzes do uniform
	global idColor
	global idViewPos
	global idLight
	global idLightPos
	
	# variaveis das forcas do reflections
	global ambientForce
	global diffuseForce
	global specularForce

	
	


	glClearColor(0, 0, 0, 1)

	for i in lista_obj: # percorre a lista dos objetos, verificando os atributos das reflectons
		if(i.ambient == 1 or i.diffuse == 1 or i.specular == 1):
			# caso tenha sido feito o comando reflection atribuimos 1 para a flag e chamando o shaders das reflections
			reflectionFlag = 1
			vertex_code = readShaderFile('reflect.vp')
			fragment_code = readShaderFile('reflect.fp')
		else:
			vertex_code = readShaderFile('none.vp')
			fragment_code = readShaderFile('none.fp')

	# compile shaders and program
	vertexShader = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
	fragmentShader = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
	shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)
	
	# Create and bind the Vertex Array Object
	vao = GLuint(0)
	glGenVertexArrays(1, vao)
	glBindVertexArray(vao)
	
    # lendo os obj pegando vertices e normais
	vertices = np.array(lendo_obj(obj), dtype='f')
	print("vertices:", len(vertices)//6)
	
	vbo = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vbo)
	glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
	glVertexAttribPointer(0, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), ctypes.c_void_p(3*sizeof(GLfloat)))  # first 0 is the location in shader
	glVertexAttribPointer(1, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), ctypes.c_void_p(0))  # first 0 is the location in shader
	glEnableVertexAttribArray(0)  
	glEnableVertexAttribArray(1)  

	#verifica em cada objeto a scala 
	for i in lista_obj:
		i.model = pyrr.matrix44.create_identity()
		scale = pyrr.matrix44.create_from_scale([i.scale_r, i.scale_g, i.scale_b],dtype='f')
		i.model = pyrr.matrix44.multiply(i.model,scale)


	#verifica em cada objeto se precisa fazer rotacao
	for i in lista_obj:
		if(i.rotate_x == 1):
			rotx = pyrr.matrix44.create_from_x_rotation(math.radians(i.rotate_grau))
		else:
			rotx = pyrr.matrix44.create_from_x_rotation(math.radians(0))

		if(i.rotate_y == 1):
			rotY = pyrr.matrix44.create_from_y_rotation(math.radians(i.rotate_grau))
		else:
			rotY = pyrr.matrix44.create_from_y_rotation(math.radians(0))

		if(i.rotate_z == 1):
			rotZ = pyrr.matrix44.create_from_z_rotation(math.radians(i.rotate_grau))
		else:
			rotZ = pyrr.matrix44.create_from_z_rotation(math.radians(0))


		rotT = pyrr.matrix44.multiply(rotY,rotx)
		rotT = pyrr.matrix44.multiply(rotT,rotZ)
		i.model =pyrr.matrix44.multiply(i.model,rotT)

	#verifica em cada objeto a translacao
	for i in lista_obj:
		translate = pyrr.matrix44.create_from_translation([i.translate_x,i.translate_y,i.translate_z])
		i.model = pyrr.matrix44.multiply(i.model,translate)

	#coloca os valores da view
	view = matrix44.create_look_at(poscam, lookat, [0.0, 1.0, 0.0])
	#redimenciona o mundo 
	projection = matrix44.create_orthogonal_projection(-2.0, 2.0, -2.0, 2.0, 2.0, -2.0)
	
	
	# atribui uma variavel uniforme para matriz de transformacao
	uMat = glGetUniformLocation(shaderProgram, "model")
	#atribui uma variavel uniforme para view
	idView = glGetUniformLocation(shaderProgram, "view")
	#atribui uma variavel uniform para projection
	idProj = glGetUniformLocation(shaderProgram, "projection")

	# verificando se a reflections foi ativada
	if(reflectionFlag == 1):
		# atribuindo os uniformes para uma variavel 
		idColor = glGetUniformLocation(shaderProgram, "objectColor")
		idLight = glGetUniformLocation(shaderProgram, "lightColor")
		idLightPos = glGetUniformLocation(shaderProgram, "lightPos")
		idViewPos = glGetUniformLocation(shaderProgram, "viewPos")
		reflec = glGetUniformLocation(shaderProgram, "reflecc")
		ambientForce = glGetUniformLocation(shaderProgram, "ambientForce")
		diffuseForce = glGetUniformLocation(shaderProgram, "diffuseForce")
		specularForce = glGetUniformLocation(shaderProgram, "specularForce")

	

	# Note that this is allowed, the call to glVertexAttribPointer registered VBO
	# as the currently bound vertex buffer object so afterwards we can safely unbind
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	# Unbind VAO (it's always a good thing to unbind any buffer/array to prevent strange bugs)
	glBindVertexArray(0)

# funcao que desenha a luz
def drawlight(lista_luz):
	global shaderProgram
	global vao
	global vbo
	global projection
	global idProj
	global idView
	global model
	global view
	global uMat
	global poscam
	global lookat
	global ambient
	global diffuse
	global specular
	global lightMode

	glClearColor(0, 0, 0, 1)

	vertex_code = readShaderFile('none.vp')
	fragment_code = readShaderFile('none.fp')

	# compile shaders and program
	vertexShader = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
	fragmentShader = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
	shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)
	
	# Create and bind the Vertex Array Object
	vao = GLuint(0)
	glGenVertexArrays(1, vao)
	glBindVertexArray(vao)
	
	obj = 'cube'
    # lendo os obj pegando vertices e normais
	vertices = np.array(lendo_obj(obj), dtype='f')
	print("vertices:", len(vertices)//6)

	
	vbo = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vbo)
	glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
	glVertexAttribPointer(0, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), ctypes.c_void_p(3*sizeof(GLfloat)))  # first 0 is the location in shader
	glVertexAttribPointer(1, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), ctypes.c_void_p(0))  # first 0 is the location in shader
	glEnableVertexAttribArray(0)  
	glEnableVertexAttribArray(1)

	#verifica em cada objeto a scala 
	for i in lista_luz:
		i.model = pyrr.matrix44.create_identity()
		scale = pyrr.matrix44.create_from_scale([0.03, 0.03, 0.03],dtype='f')
		i.model = pyrr.matrix44.multiply(i.model,scale)



	#verifica em cada objeto a translacao
	for i in lista_luz:
		translate = pyrr.matrix44.create_from_translation([i.x,i.y,i.z])
		i.model = pyrr.matrix44.multiply(i.model,translate)

	#coloca os valores da view
	view = matrix44.create_look_at(poscam, lookat, [0.0, 1.0, 0.0])
	#redimenciona o mundo 
	projection = matrix44.create_orthogonal_projection(-2.0, 2.0, -2.0, 2.0, 2.0, -2.0)
	
	
	# atribui uma variavel uniforme para matriz de transformacao
	uMat = glGetUniformLocation(shaderProgram, "model")
	#atribui uma variavel uniforme para view
	idView = glGetUniformLocation(shaderProgram, "view")
	#atribui uma variavel uniform para projection
	idProj = glGetUniformLocation(shaderProgram, "projection")

	

	# Note that this is allowed, the call to glVertexAttribPointer registered VBO
	# as the currently bound vertex buffer object so afterwards we can safely unbind
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	# Unbind VAO (it's always a good thing to unbind any buffer/array to prevent strange bugs)
	glBindVertexArray(0)


#desenha os eixos x y z
def drawAxis():
	global shaderProgram
	global vao
	global vbo
	global model
	global uMat
	global view
	global idProj
	global idView
	global projection

	glClearColor(0, 0, 0, 1)
	
	# carrega os shaders do axis
	vertex_code = readShaderFile('axis.vp')
	fragment_code = readShaderFile('axis.fp')

	# compila o shaders e program
	vertexShader = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
	fragmentShader = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
	shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)
	
	# cria e faz o bind no vertex arrat object
	vao = GLuint(0)
	glGenVertexArrays(1, vao)
	glBindVertexArray(vao)
	
	#vertices
	x = np.array([[255,0,0], [ 0, 0 ,0], [-255, 0, 0]],dtype='f')
	y = np.array([[0,255, 0], [ 0, 0, 0], [0, -255, 0]],dtype='f')
	z = np.array([[0 ,0, 255], [ 0, 0, 0], [0, 0, -255]],dtype='f') 
	vertices = np.concatenate((x,y,z))

	vbo = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vbo)
	glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
	glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)  # first 0 is the location in shader
	glBindAttribLocation(shaderProgram, 0, 'vertexPosition')
	glEnableVertexAttribArray(0); 

	view = matrix44.create_look_at(poscam, lookat, [0.0, 1.0, 0.0])
	projection = matrix44.create_orthogonal_projection(-2.0, 2.0, -2.0, 2.0, 2.0, -2.0)

	idView = glGetUniformLocation(shaderProgram, "view")
	idProj = glGetUniformLocation(shaderProgram, "projection")
	
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	glBindVertexArray(0)

def draw(lista_obj,axis,lista_luz):
	global shaderProgram
	global vao
	global reflectionFlag

	for i in lista_obj: #varre a lista de objetos
		#desenha o cubo
		if(i.shape == 'cube'):
			init(i.shape,lista_obj) #manda o .obj que vai ser carregado e a lista dos objetos
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			if(reflectionFlag == 1): 	# verifica se o reflections esta ativo
				for x in lista_luz: # percorre a lista das luzes
					# passa as informacoes para os shaders 
					glUniform3fv(idLightPos, 1,x.x,x.y,x.z)
					glUniform3fv(idColor,1,[i.r,i.g,i.b])
					glUniform3fv(idLight,1,[1.0,1.0,1.0])
					glUniform3fv(reflec,1,[i.ambient, i.diffuse, i.specular])
					glUniform3fv(ambientForce,1,[i.ambientForce])
					glUniform3fv(diffuseForce,1,[i.diffuseForce])
					glUniform3fv(specularForce,1,[i.specularForce])
					glUniform3fv(idViewPos,1,poscam)

			# passa as transformacoes para os shaders
			glUniformMatrix4fv(uMat, 1, GL_FALSE, i.model)
			glUniformMatrix4fv(idView, 1, GL_FALSE, view)
			glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)

			Color = glGetUniformLocation(shaderProgram,"uColor")
			glUniform3f(Color,i.r, i.g, i.b) # atribuindo a cor 
			if(i.wireMode == 1): #verifica se esta habilitado o wiremode
				glDrawArrays(GL_LINE_LOOP, 0, 42)
			else:
				glDrawArrays(GL_TRIANGLES, 0, 42) #desenhando o cubo

			#desenha torus
		elif(i.shape == 'torus'):
			init(i.shape,lista_obj) #manda o .obj que vai ser carregado e a lista dos objetos
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			if(reflectionFlag == 1): # verifica se o reflections esta ativo
				for x in lista_luz:# percorre a lista das luzes
				#passa as informacoes para os shaders 
					glUniform3fv(idLightPos, 1,x.x,x.y,x.z)
					glUniform3fv(idColor,1,[i.r,i.g,i.b])
					glUniform3fv(idLight,1,[1.0,1.0,1.0])
					glUniform3fv(reflec,1,[i.ambient, i.diffuse, i.specular])
					glUniform3fv(ambientForce,1,[i.ambientForce])
					glUniform3fv(diffuseForce,1,[i.diffuseForce])
					glUniform3fv(specularForce,1,[i.specularForce])
					glUniform3fv(idViewPos,1,poscam)

			#passa as tranformacoes para os shaders
			glUniformMatrix4fv(uMat, 1, GL_FALSE, i.model)
			glUniformMatrix4fv(idView, 1, GL_FALSE, view)
			glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)
		
			Color = glGetUniformLocation(shaderProgram,"uColor")
			glUniform3f(Color,i.r,i.g,i.b) # atribuindo a cor 
			if(i.wireMode == 1): #verifica se o wireMode esta ativo
				glDrawArrays(GL_LINES, 0, 3462)
			else:
				glDrawArrays(GL_TRIANGLES, 0, 3462) 

		#desenha cone
		elif(i.shape == 'cone'):	
			init(i.shape,lista_obj) #manda o .obj que vai ser carregado e a lista dos objetos
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			if(reflectionFlag == 1): # verifica se o reflections esta ativo
				for x in lista_luz: # percorre a lista das luzes
				#passa as informacoes para os shaders 
					glUniform3fv(idLightPos, 1,x.x,x.y,x.z)
					glUniform3fv(idColor,1,[i.r,i.g,i.b])
					glUniform3fv(idLight,1,[1.0,1.0,1.0])
					glUniform3fv(reflec,1,[i.ambient, i.diffuse, i.specular])
					glUniform3fv(ambientForce,1,[i.ambientForce])
					glUniform3fv(diffuseForce,1,[i.diffuseForce])
					glUniform3fv(specularForce,1,[i.specularForce])
					glUniform3fv(idViewPos,1,poscam)
			#passa as tranformacoes para os shaders
			glUniformMatrix4fv(uMat, 1, GL_FALSE, i.model)
			glUniformMatrix4fv(idView, 1, GL_FALSE, view)
			glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)
			Color = glGetUniformLocation(shaderProgram,"uColor")
			glUniform3f(Color,i.r, i.g, i.b) # atribuindo a cor	
			if(i.wireMode == 1 ): # verifica se o wireMode esta ativo
				glDrawArrays(GL_LINES, 0, 276)
			else:
				glDrawArrays(GL_TRIANGLES, 0, 276)
				

			#desenha esfera
		elif(i.shape == 'sphere'):
			init(i.shape,lista_obj) #manda o .obj que vai ser carregado e a lista dos objetos
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			if(reflectionFlag == 1): # verifica se o reflections esta ativo
				for x in lista_luz: # percorre a lista das luzes
				#passa as informacoes para os shaders
					glUniform3fv(idLightPos, 1,x.x,x.y,x.z)
					glUniform3fv(idColor,1,[i.r,i.g,i.b])
					glUniform3fv(idLight,1,[1.0,1.0,1.0])
					glUniform3fv(reflec,1,[i.ambient, i.diffuse, i.specular])
					glUniform3fv(ambientForce,1,[i.ambientForce])
					glUniform3fv(diffuseForce,1,[i.diffuseForce])
					glUniform3fv(specularForce,1,[i.specularForce])
					glUniform3fv(idViewPos,1,poscam)

			#passa as tranformacoes para os shaders
			glUniformMatrix4fv(uMat, 1, GL_FALSE, i.model)
			glUniformMatrix4fv(idView, 1, GL_FALSE, view)
			glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)
			Color = glGetUniformLocation(shaderProgram,"uColor")
			glUniform3f(Color,i.r, i.g, i.b) # atribuindo a cor 
			if(i.wireMode == 1): # verifica se o wireMode esta ativo
				glDrawArrays(GL_LINES, 0, 15363)
			else:
				glDrawArrays(GL_TRIANGLES, 0, 15363)

	for i in lista_luz:
		drawlight(lista_luz)
		glUseProgram(shaderProgram)
		glBindVertexArray(vao)
		glBindBuffer(GL_ARRAY_BUFFER, vbo)
		glUniformMatrix4fv(uMat, 1, GL_FALSE, i.model)
		glUniformMatrix4fv(idView, 1, GL_FALSE, view)
		glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)
		Color = glGetUniformLocation(shaderProgram,"uColor")
		glUniform3f(Color,1,1,0) # atribuindo a cor
		if(i.lightMode == 1):
			glDrawArrays(GL_TRIANGLES, 0, 42)



	#desenha os eixos
	if(axis == 1):
		drawAxis()
		glUseProgram(shaderProgram)
		glBindVertexArray(vao)
		glBindBuffer(GL_ARRAY_BUFFER, vbo)
		glUniformMatrix4fv(idView, 1, GL_FALSE, view)
		glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)
		Color = glGetUniformLocation(shaderProgram,"uColor")
		glUniform3f(Color, 1, 0, 0)
		glDrawArrays(GL_LINE_LOOP, 0, 3)
		glUniform3f(Color, 0, 1, 0)
		glDrawArrays(GL_LINE_LOOP, 3, 3)
		glUniform3f(Color, 0, 0, 1)
		glDrawArrays(GL_LINE_LOOP, 6, 3)

class obj_light(object):
	nome = ""

	def __init__(self,nome,x,y,z,model,lightMode):
		self.nome = nome
		self.x = x
		self.y = y
		self.z = z
		self.model = model
		self.lightMode = lightMode

	def nome(self):
		return self.nome

	#posicao
	def x(self):
		return self.x
	def y(self):
		return self.y
	def z(self):
		return self.z

	# model
	def model(self):
		return self.model

	#on e off
	def lightMode(self):
		return self.lightMode

#classe para armazenar os objetos
class objeto(object):
	shape = ""
	nome = ""
	model = 0
	wireMode = 0
	
	

	def __init__(self, shape, nome,r,g,b, model, wireMode,scale_r,scale_g,scale_b,rotate_grau,rotate_x,rotate_y,rotate_z,translate_x,translate_y,translate_z,cam_x,cam_y,cam_z,ambient,diffuse,specular,ambientForce,diffuseForce,specularForce):
		self.shape = shape
		self.nome = nome
		self.r = r
		self.g = g
		self.b = b
		self.model = model
		self.wireMode = wireMode
		self.scale_r = scale_r
		self.scale_g = scale_g
		self.scale_b = scale_b
		self.rotate_grau = rotate_grau
		self.rotate_x = rotate_x
		self.rotate_y = rotate_y
		self.rotate_z = rotate_z
		self.translate_x = translate_x
		self.translate_y = translate_y
		self.translate_z = translate_z
		self.cam_x = cam_x
		self.cam_y = cam_y
		self.cam_z = cam_z
		self.ambient = ambient
		self.diffuse = diffuse
		self.specular = specular
		self.ambientForce = ambientForce
		self.diffuseForce = diffuseForce
		self.specularForce = specularForce

	
	def nome(self):
		return self.nome

	def shape(self):
		return self.shape
	#cores
	def r(self):
		return self.r
	def g(self):
		return self.g
	def b(self):
		return self.b

	# model
	def model(self):
		return self.model
	#wire
	def wireMode(self):
		return self.wireMode

	#escala
	def scale_r(self):
		return self.scale_r
	def scale_g(self):
		return self.scale_g
	def scale_b(self):
		return self.scale_b

	#rotacao
	def rotate_grau(self):
		return self.rotate_grau
	def rotate_x(self):
		return self.rotate_x
	def rotate_y(self):
		return self.rotate_y
	def rotate_z(self):
		return self.rotate_z

	#translacao
	def translate_x(self):
		return self.translate_x
	def translate_y(self):
		return self.translate_y
	def translate_z(self):
		return self.translate_z

	#camera
	def cam_x(self):
		return self.cam_x
	def cam_y(self):
		return self.cam_y
	def cam_z(self):
		return self.cam_z

	#reflections
	def ambient(self):
		return self.ambient
	def diffuse(self):
		return self.diffuse
	def specular(self):
		return self.specular

	#forca das reflections
	def ambientForce(self):
		return self.ambientForce
	def diffuseForce(self):
		return self.diffuseForce
	def specularForce(self):
		return self.specularForce
	

def display():
	#varivais para o lookat e cam
	global poscam
	global lookat
	# variaveis para on e off
	global vet_axis
	global axisFlag
	global wireMode
	global lightMode
	# variaveis para uso dos reflections
	global ambient
	global diffuse
	global specular
	

	glEnable(GL_DEPTH_TEST);
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	i = 0
	vet_obj = [] #vetor que pega os comandos do arquivo
	lista_obj = [] #lista dos objetos 
	lista_luz = [] #lista das luzes
	modelDefault = pyrr.matrix44.create_identity()#carrega a varivavel com a matriz identidae 
	arq = sys.argv[1]

	arquivo = open(arq,'r')# le arquivo dos comandos
	for linha in arquivo:
		linha = linha.replace('\n','')# adiciona oscomando para variavel linha

		for i in linha.split():# quebra o comando em partes e adiciona para a lista de obj
			vet_obj.append(i)

			print(vet_obj)

	for i in range(len(vet_obj)):
		if(vet_obj[i] == 'add_shape'): #verifica se existe o comando add_shape
			aux = objeto(vet_obj[i+1],vet_obj[i+2],1,1,1,modelDefault,wireMode,1,1,1, 0,0,0,0, 0,0,0, 0,0,0, 0,0,0, 0.1,1,0.5)
			lista_obj.append(aux) #cria o objeto a ser desenhado
			
			
		elif(vet_obj[i] == 'color'): #verifica se existe o comando color
			for x in lista_obj:
				if(x.nome == vet_obj[i+1]):
					x.r = float(vet_obj[i+2])
					x.g = float(vet_obj[i+3])
					x.b = float(vet_obj[i+4])
	
		#verifica se existe o comando wire_on para ativar
		elif(vet_obj[i] == 'wire_on'):
			for x in lista_obj: #percorre a lista dos objetos e modifica o atributo wireMode para 1
				wireMode = 1
				x.wireMode = wireMode
				
		#verifica se existe o comando wire_off para ativar
		elif(vet_obj[i] == 'wire_off'):
			for x in lista_obj: #percorre a lista dos objetos e modifica o atributo wireMode para 0
				wireMode = 0
				x.wireMode = wireMode

		#verifica se existe o comando remove_shape para executar
		elif(vet_obj[i] == 'remove_shape'):
			for x in lista_obj: #percorre a lista dos objetos e verifica se o nome que foi passado existe na lista para remover
				if(x.nome == vet_obj[i+1]):
					lista_obj.remove(x)

		#verifica se existe o comando axis_on para ativar mudando a variavel global para 1 
		elif(vet_obj[i] == 'axis_on'):
			if(axisFlag == 0):
				vet_axis = 1
				axisFlag = 1
		#verifica se existe o comando axis_off para ativar mudando a variavel global para 0		
		elif(vet_obj[i] == 'axis_off'):
			if(axisFlag == 1):
				vet_axis = 0
				axisFlag = 0

		#verifica se existe o comando scale 
		elif(vet_obj[i] == 'scale'):
			for x in lista_obj: #percorre a lista dos objetos, procurando o nome que foi passado para mudar os atributo de escala de cada objeto
				if(x.nome == vet_obj[i+1]):
					x.scale_r = float(vet_obj[i+2])
					x.scale_g = float(vet_obj[i+3])
					x.scale_b = float(vet_obj[i+4])

		#verifica se existe o comando rotate
		elif(vet_obj[i] == 'rotate'):
			for x in lista_obj: #percorre a lista de objetos, procurando o nome que foi passado e modifica os atributos rotate de cada objeto
				if(x.nome == vet_obj[i+1]):
					x.rotate_grau = int(vet_obj[i+2])
					x.rotate_x = float(vet_obj[i+3])
					x.rotate_y = float(vet_obj[i+4])
					x.rotate_z = float(vet_obj[i+5])
		# verifica se existe o comando translate
		elif(vet_obj[i] == 'translate'):
			for x in lista_obj: #percorre a lista de objetos, procurando o nome que foi passado e modificando o atributo translate de cada objeto
				if(x.nome == vet_obj[i+1]):
					x.translate_x = float(vet_obj[i+2])
					x.translate_y = float(vet_obj[i+3])
					x.translate_z = float(vet_obj[i+4])

		#verifica se existe o comando cam
		elif(vet_obj[i] == 'cam'):
			# atribuiu a posicao a variavel global poscam
			poscam = [float(vet_obj[i+1]),float(vet_obj[i+2]),float(vet_obj[i+3])]

		# verifica se existe o comando lookat
		elif(vet_obj[i] == 'lookat'):
			# atribui a posicao a variavel global lookat
			lookat = [float(vet_obj[i+1]),float(vet_obj[i+2]),float(vet_obj[i+3])]

		# verifica se existe o comando remove_light
		elif(vet_obj[i] == 'remove_light'):
			for x in lista_luz: #percorre a lista de luzes, procurando o nome que foi passado e retira ela da lista
				if(x.nome == vet_obj[i+1]):
					lista_luz.remove(x)

		# verifica se existe o comando add_light 
		elif(vet_obj[i] == 'add_light'):
			# coloca a nova luz na lista de luzes
			aux = obj_light(vet_obj[i+1],float(vet_obj[i+2]),float(vet_obj[i+3]),float(vet_obj[i+4]),modelDefault,lightMode)
			lista_luz.append(aux)

		# verifica se existe o comando lights_on
		elif(vet_obj[i] == 'lights_on'):
			for x in lista_luz: #percorre a lista de luzes modificando o atributo lightMode para 1 de cada luz
				lightMode = 1
				x.lightMode = lightMode

		# verifica se existe o comando lights_off
		elif(vet_obj[i] == 'lights_off'):
			for x in lista_luz: #percorre a lista de luzes modificando o atributo lightMode para 0 de cada luz
				lightMode = 0
				x.lightMode = lightMode

		# verifica se existe o comando reflection_on
		elif(vet_obj[i] == 'reflection_on'):
			for x in lista_obj: 
				# percorre a lista de objetos, verificando o nome que foi passado e modificando o atributo junto com a sua forca
				if(vet_obj[i+1] == 'ambient'):
					x.ambient = 1
					x.ambientForce = float(vet_obj[i+2])

				elif(vet_obj[i+1] == 'diffuse'):
					x.diffuse = 1
					x.diffuseForce = float(vet_obj[i+2])

				elif(vet_obj[i+1] == 'specular'):
					x.specular = 1
					x.specularForce = float(vet_obj[i+2])

		#verifica se existe o comando reflection_off
		elif(vet_obj[i] == 'reflection_off'):
			for x in lista_obj:
				#percorre a lista de objetos, verificando o nome que foi passado e modificando o atributo para 0
				if(vet_obj[i+1] == 'ambient'):
					x.ambient = 0

				elif(vet_obj[i+1] == 'diffuse'):
					x.diffuse = 0

				elif(vet_obj[i+1] == 'specular'):
					x.specular = 0


		#verificando se existe o comando save
		elif(vet_obj[i] == 'save'):

			glPixelStorei(GL_PACK_ALIGNMENT,1) #guarda os pixels
			data = glReadPixels(0,0,640,640,GL_RGBA,GL_UNSIGNED_BYTE) # le os pixels da tela
			image = Image.frombytes("RGBA",(640,640),data) #cria a imagem
			image = image.transpose(Image.FLIP_TOP_BOTTOM) #flipa a imagem, pois estava de cabeca para baixo

			image.save(vet_obj[i+1]+'.png','png') # salva a imagem em png

		# verifica se existe o comando quit
		elif(vet_obj[i] == 'quit'):
			glutLeaveMainLoop() # interrope o loop
			glutDestroyWindow() #destroi a janela criada


					


	draw(lista_obj,vet_axis,lista_luz) #chama a funcao que desenha
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	glBindVertexArray(0)
	glUseProgram(0)
	glReadBuffer(GL_FRONT)
	glutSwapBuffers()  

def reshape(width, height):
	glViewport(0, 0, width, height)


if __name__ == '__main__':
	glutInit(sys.argv)
	glutInitContextVersion(3, 0)
	glutInitContextProfile(GLUT_CORE_PROFILE);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
	
	glutInitWindowSize(640, 640);
	glutCreateWindow(b'Trabalho')
	
	glutReshapeFunc(reshape)
	glutDisplayFunc(display)
	glutIdleFunc(display)
	
	
	
	glutMainLoop()


