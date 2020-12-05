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
from PIL import Image

vao = None
vbo = None
shaderProgram = None
uMat = None       
projection = None #variavel projection 
view = None    #variavel view
model = None   #variavel model
idProj = None   
idView = None     
rotate = 0
poscam = [0,0,0] #camera default
lookat = [0,0,-1] #lookt default
ambient = 0
specular = 0
diffuse = 0
lightMode = 1
wireMode = 0
axisFlag = 0
vet_axis = 0

def readObjFile(path):
	return obj.Wavefront(path)

def readVertexData():
	aux = readObjFile('cube.obj')
	aux.parse()
	for name, material in aux.materials.items():
		return material.vertices

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
	

    # lendo os obj pegando vertices e normais
	vertices = np.array(lendo_obj(obj), dtype='f')
	print("vertices:", len(vertices)//6)
	#print(vertices)

	
	vbo = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vbo)
	glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
	glVertexAttribPointer(0, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), ctypes.c_void_p(3*sizeof(GLfloat)))  # first 0 is the location in shader
	glVertexAttribPointer(1, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), ctypes.c_void_p(0))  # first 0 is the location in shader
	#glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)  # first 0 is the location in shader
	#glBindAttribLocation(shaderProgram, 0, 'vertexPosition')  # name of attribute in shader
	glEnableVertexAttribArray(0)  # 0=location do atributo, tem que ativar todos os atributos inicialmente sao desabilitados por padrao
	glEnableVertexAttribArray(1)  # 0=location do atributo, tem que ativar todos os atributos inicialmente sao desabilitados por padrao
	# cria a matriz de transformação

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

	

	# Note that this is allowed, the call to glVertexAttribPointer registered VBO
	# as the currently bound vertex buffer object so afterwards we can safely unbind
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	# Unbind VAO (it's always a good thing to unbind any buffer/array to prevent strange bugs)
	glBindVertexArray(0)
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
	#print(vertices)

	
	vbo = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vbo)
	glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
	glVertexAttribPointer(0, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), ctypes.c_void_p(3*sizeof(GLfloat)))  # first 0 is the location in shader
	glVertexAttribPointer(1, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), ctypes.c_void_p(0))  # first 0 is the location in shader
	#glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)  # first 0 is the location in shader
	#glBindAttribLocation(shaderProgram, 0, 'vertexPosition')  # name of attribute in shader
	glEnableVertexAttribArray(0)  # 0=location do atributo, tem que ativar todos os atributos inicialmente sao desabilitados por padrao
	glEnableVertexAttribArray(1)  # 0=location do atributo, tem que ativar todos os atributos inicialmente sao desabilitados por padrao
	# cria a matriz de transformação

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
	
	vertex_code = readShaderFile('axis.vp')
	fragment_code = readShaderFile('axis.fp')

	# compile shaders and program
	vertexShader = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
	fragmentShader = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
	shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)
	
	# Create and bind the Vertex Array Object
	vao = GLuint(0)
	glGenVertexArrays(1, vao)
	glBindVertexArray(vao)
	
	#vertices
	x = np.array([[255,0,0], [ 0, 0 ,0], [-255, 0, 0]],dtype='f')
	y = np.array([[0,255, 0], [ 0, 0, 0], [0, -255, 0]],dtype='f')
	z = np.array([[0 ,0, 255], [ 0, 0, 0], [0, 0, -255]],dtype='f') 
    # lendo os obj pegando vertices e normais
	vertices = np.concatenate((x,y,z))
	#print(vertices)

	
	vbo = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vbo)
	glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
	glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)  # first 0 is the location in shader
	glBindAttribLocation(shaderProgram, 0, 'vertexPosition')
	glEnableVertexAttribArray(0); 

	
	#transformacao pela view
	view = matrix44.create_look_at(poscam, lookat, [0.0, 1.0, 0.0])
	projection = matrix44.create_orthogonal_projection(-2.0, 2.0, -2.0, 2.0, 2.0, -2.0)


	idView = glGetUniformLocation(shaderProgram, "view")
	idProj = glGetUniformLocation(shaderProgram, "projection")
	# Note that this is allowed, the call to glVertexAttribPointer registered VBO
	# as the currently bound vertex buffer object so afterwards we can safely unbind
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	# Unbind VAO (it's always a good thing to unbind any buffer/array to prevent strange bugs)
	glBindVertexArray(0)

def draw(lista_obj,axis,lista_luz):
	global shaderProgram
	global vao

	for i in lista_obj: #varre a lista de objetos
		#desenha o cubo
		if(i.shape == 'cube'):
			init(i.shape,lista_obj) #manda o .obj que vai ser carregado
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
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
			init(i.shape,lista_obj) 
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			glUniformMatrix4fv(uMat, 1, GL_FALSE, i.model)
			glUniformMatrix4fv(idView, 1, GL_FALSE, view)
			glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)
			print(i.model)
			Color = glGetUniformLocation(shaderProgram,"uColor")
			glUniform3f(Color,i.r,i.g,i.b) # atribuindo a cor 
			if(i.wireMode == 1):
				glDrawArrays(GL_LINES, 0, 3462)
			else:
				glDrawArrays(GL_TRIANGLES, 0, 3462) 
		#desenha cone
		elif(i.shape == 'cone'):	
			init(i.shape,lista_obj) 
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			glUniformMatrix4fv(uMat, 1, GL_FALSE, i.model)
			glUniformMatrix4fv(idView, 1, GL_FALSE, view)
			glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)
			Color = glGetUniformLocation(shaderProgram,"uColor")
			glUniform3f(Color,i.r, i.g, i.b) # atribuindo a cor	
			if(i.wireMode == 1 ): 
				glDrawArrays(GL_LINES, 0, 276)
			else:
				glDrawArrays(GL_TRIANGLES, 0, 276)
				

			#desenha esfera
		elif(i.shape == 'sphere'):
			init(i.shape,lista_obj) 
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			glUniformMatrix4fv(uMat, 1, GL_FALSE, i.model)
			glUniformMatrix4fv(idView, 1, GL_FALSE, view)
			glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)
			Color = glGetUniformLocation(shaderProgram,"uColor")
			glUniform3f(Color,i.r, i.g, i.b) # atribuindo a cor 
			if(i.wireMode == 1):
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
		glUniform3f(Color, 0, 1, 0)
		glDrawArrays(GL_LINE_LOOP, 0, 3)
		glUniform3f(Color, 1, 0, 0)
		glDrawArrays(GL_LINE_LOOP, 3, 3)
		glUniform3f(Color, 0, 0, 1)
		glDrawArrays(GL_LINE_LOOP, 6, 3)
			



				
			


'''def draw(shape,color_obj,nome):
	global shaderProgram
	global vao
	for i in range(len(shape)): # varre a lista de formas
		if(shape[i] == 'cube'): # verifica se existe um cubo
				auxColor = color_obj[i] # pega a cor se for passado pelo comando color caso nao exista usa a cor padrao branca
				init(shape[i]) # chama funcao que instancia os vbo e vao
				glUseProgram(shaderProgram)
				glBindVertexArray(vao)
				glBindBuffer(GL_ARRAY_BUFFER, vbo)
				glUniformMatrix4fv(uMat, 1, GL_FALSE, model)
				Color = glGetUniformLocation(shaderProgram,"uColor")
				print(auxColor[0])
				print(auxColor[1])
				print(auxColor[2])
				glUniform3f(Color, auxColor[0],auxColor[1],auxColor[2]) # atribuindo a cor 
				glDrawArrays(GL_TRIANGLES, 0, 36) #desenhando o cubo
			
			
		elif(shape[i] == 'torus'):
			init(shape[i])
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			glUniformMatrix4fv(uMat, 1, GL_FALSE, model)
			glDrawArrays(GL_TRIANGLES, 0, 3462)
		elif(shape[i] == 'ico'):
			init(shape[i])
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			glUniformMatrix4fv(uMat, 1, GL_FALSE, model)
			glDrawArrays(GL_TRIANGLES, 0, 15363)
		elif(shape[i] == 'cone'):
			init(shape[i])
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			glUniformMatrix4fv(uMat, 1, GL_FALSE, model)
			glDrawArrays(GL_TRIANGLES, 0, 276)'''

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

	def x(self):
		return self.x

	def y(self):
		return self.y

	def z(self):
		return self.z

	def model(self):
		return self.model

	def lightMode(self):
		return self.lightMode

#classe para armazenar os objetos
class objeto(object):
	shape = ""
	nome = ""
	model = 0
	wireMode = 0
	
	

	def __init__(self, shape, nome,r,g,b, model, wireMode,scale_r,scale_g,scale_b,rotate_grau,rotate_x,rotate_y,rotate_z,translate_x,translate_y,translate_z,cam_x,cam_y,cam_z):
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

	

	def nome(self):
		return self.nome

	def shape(self):
		return self.shape

	def r(self):
		return self.r

	def g(self):
		return self.g

	def b(self):
		return self.b

	def model(self):
		return self.model

	def wireMode(self):
		return self.wireMode

	def scale_r(self):
		return self.scale_r

	def scale_g(self):
		return self.scale_g

	def scale_b(self):
		return self.scale_b

	def rotate_grau(self):
		return self.rotate_grau

	def rotate_x(self):
		return self.rotate_x

	def rotate_y(self):
		return self.rotate_y

	def rotate_z(self):
		return self.rotate_z


	def translate_x(self):
		return self.translate_x

	def translate_y(self):
		return self.translate_y

	def translate_z(self):
		return self.translate_z

	def cam_x(self):
		return self.cam_x

	def cam_y(self):
		return self.cam_y

	def cam_z(self):
		return self.cam_z






"""#cria o objeto que vai ser desenhado
def objeto(shape,nome,cor,model,wireMode):

	objeto = {"shape":shape,
			  "nome":nome,
			  "cor":cor,
			  "model":model,
			  "wireMode":wireMode}

	return objeto"""


def display():
	global vet_axis
	global axisFlag
	global poscam
	global lookat
	global wireMode
	global lightMode
	global ambient
	global diffuse
	global specular

	glEnable(GL_DEPTH_TEST);
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	
	# load everthing back
	i = 0
	vet_obj = []
	vet_cor = [1,1,1]
	lista_obj = []
	lista_luz = []
	scaleDefault = [1,1,1]

	
	colorDefault = [1,1,1]
	modelDefault = pyrr.matrix44.create_identity()
	arq = sys.argv[1]

	arquivo = open(arq,'r')# le arquivo dos comandos
	for linha in arquivo:
		linha = linha.replace('\n','')# adiciona oscomando para variavel linha

		for i in linha.split():# quebra o comando em partes e adiciona para a lista de obj
			vet_obj.append(i)

			print(vet_obj)

	for i in range(len(vet_obj)):
		if(vet_obj[i] == 'add_shape'): #verifica se existe o comando add_shape
			aux = objeto(vet_obj[i+1],vet_obj[i+2],1,1,1,modelDefault,wireMode,1,1,1, 0,0,0,0, 0,0,0, 0,0,0)
			lista_obj.append(aux) #cria o objeto a ser desenhado
			
			
		elif(vet_obj[i] == 'color'): #verifica se existe o comando color
			for x in lista_obj:
				if(x.nome == vet_obj[i+1]):
					x.r = float(vet_obj[i+2])
					x.g = float(vet_obj[i+3])
					x.b = float(vet_obj[i+4])
	

		elif(vet_obj[i] == 'wire_on'):
			for x in lista_obj:
				wireMode = 1
				x.wireMode = wireMode
				

		elif(vet_obj[i] == 'wire_off'):
			for x in lista_obj:
				wireMode = 0
				x.wireMode = wireMode

		elif(vet_obj[i] == 'remove_shape'):
			for x in lista_obj:
				if(x.nome == vet_obj[i+1]):
					lista_obj.remove(x)

		elif(vet_obj[i] == 'axis_on'):
			if(axisFlag == 0):
				vet_axis = 1
				axisFlag = 1
		elif(vet_obj[i] == 'axis_off'):
			if(axisFlag == 1):
				vet_axis = 0
				axisFlag = 0

		elif(vet_obj[i] == 'scale'):
			for x in lista_obj:
				if(x.nome == vet_obj[i+1]):
					x.scale_r = float(vet_obj[i+2])
					x.scale_g = float(vet_obj[i+3])
					x.scale_b = float(vet_obj[i+4])

		elif(vet_obj[i] == 'rotate'):
			for x in lista_obj:
				if(x.nome == vet_obj[i+1]):
					x.rotate_grau = int(vet_obj[i+2])
					x.rotate_x = float(vet_obj[i+3])
					x.rotate_y = float(vet_obj[i+4])
					x.rotate_z = float(vet_obj[i+5])

		elif(vet_obj[i] == 'translate'):
			for x in lista_obj:
				if(x.nome == vet_obj[i+1]):
					x.translate_x = float(vet_obj[i+2])
					x.translate_y = float(vet_obj[i+3])
					x.translate_z = float(vet_obj[i+4])

		elif(vet_obj[i] == 'cam'):
			poscam = [float(vet_obj[i+1]),float(vet_obj[i+2]),float(vet_obj[i+3])]
			print(poscam)

		elif(vet_obj[i] == 'lookat'):
			lookat = [float(vet_obj[i+1]),float(vet_obj[i+2]),float(vet_obj[i+3])]


		elif(vet_obj[i] == 'remove_light'):
			for x in lista_luz:
				if(x.nome == vet_obj[i+1]):
					lista_luz.remove(x)

		elif(vet_obj[i] == 'add_light'):
			aux = obj_light(vet_obj[i+1],float(vet_obj[i+2]),float(vet_obj[i+3]),float(vet_obj[i+4]),modelDefault,lightMode)
			lista_luz.append(aux)

		elif(vet_obj[i] == 'lights_on'):
			for x in lista_luz:
				lightMode = 1
				x.lightMode = lightMode

		elif(vet_obj[i] == 'lights_off'):
			for x in lista_luz:
				lightMode = 0
				x.lightMode = lightMode

		elif(vet_obj[i] == 'save'):
			glPixelStorei(GL_PACK_ALIGNMENT,1)
			data = glReadPixels(0,0,640,640,GL_RGBA,GL_UNSIGNED_BYTE)
			image = Image.frombytes("RGBA",(640,640),data)
			image.save(vet_obj[i+1]+'.png','png')


					


	draw(lista_obj,vet_axis,lista_luz) #chama a funcao que desenha
		
		#clean things up
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	glBindVertexArray(0)
	glUseProgram(0)
	glReadBuffer(GL_FRONT)
	glutSwapBuffers()  # necessario para windows!

'''def display():
	
	
	
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	
	# load everthing back
	i = 0
	vet_obj = []
	shape = []
	nome =[]
	color_obj = []
	colorDefault = ['111']
	arq = sys.argv[1]
	arquivo = open(arq,'r')# le arquivo dos comandos
	for linha in arquivo:
		linha = linha.replace('\n','')# adiciona oscomando para variavel linha
		for i in linha.split():# quebra o comando em partes e adiciona para a lista de obj
			vet_obj.append(i)
	print(i)		
	for i in range(len(vet_obj)): # varre todos os comando na lista obj
		if(vet_obj[i] == 'add_shape'): # verifica se o comando add_shape esta na lista
			color_obj.append(colorDefault) # coloca cor padrao branca 
			shape.append(vet_obj[i+1]) # pega qual e o shape para desenhar
			nome.append(vet_obj[i+2]) # pega o nome do obj
			i = i+3 #pula para o proximo comando
		elif(vet_obj[i] == 'color'): #verifica se o comando color ta na lista
			RGB = [vet_obj[i+2],vet_obj[i+3],vet_obj[i+4]] #guarda os vertices das cores
			for j in range(len(nome)): # varre os nomes dos obj
				if(vet_obj[i+1] == nome[j]):
					for x in range(len(color_obj)):
						color_obj.append(RGB)
						i = i+4 # pula o comando
						print(color_obj[j])
		
	draw(shape,color_obj,nome) #chama a funcao que desenha
		
		#clean things up
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	glBindVertexArray(0)
	glUseProgram(0)
	
	glutSwapBuffers()  # necessario para windows!'''

	
	
	
def reshape(width, height):
	glViewport(0, 0, width, height)


if __name__ == '__main__':
	glutInit(sys.argv)
	glutInitContextVersion(3, 0)
	glutInitContextProfile(GLUT_CORE_PROFILE);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
	
	glutInitWindowSize(640, 640);
	glutCreateWindow(b'cube 3D!')
	
	glutReshapeFunc(reshape)
	glutDisplayFunc(display)
	glutIdleFunc(display)
	
	
	
	glutMainLoop()

