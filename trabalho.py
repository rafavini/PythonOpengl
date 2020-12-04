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

vao = None
vbo = None
shaderProgram = None
uMat = None       
projection = None     # variavel uniforme
model = None
idProj = None        # matriz de transformação
rotate = 0
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

def init(obj):
	global shaderProgram
	global vao
	global vbo
	global projection
	global idProj
	global model
	global uMat
	
	


	glClearColor(0, 0, 0, 1)
	
	vertex_code = readShaderFile('cube.vp')
	fragment_code = readShaderFile('cube.fp')

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

	model = pyrr.matrix44.create_identity()
	#PODEMOS TIRAR ESSA PARTE DA ESCALA POIS JA ESTA FUNCIONANDO A ORTHO
	#NAO VOU TIRAR AGORA PARA PODER VER O CODIGO DEPOIS PARA FAZER A ESCALA
	scale = pyrr.matrix44.create_from_scale([0.5,0.5,0.5],dtype='f')
	model = pyrr.matrix44.multiply(model,scale)


	rotZ = pyrr.matrix44.create_from_z_rotation(math.radians(0))
	rotY = pyrr.matrix44.create_from_y_rotation(math.radians(45))
	rotx = pyrr.matrix44.create_from_x_rotation(math.radians(45))
	rotT = pyrr.matrix44.multiply(rotY,rotx)
	rotT = pyrr.matrix44.multiply(rotT,rotZ)

	model = pyrr.matrix44.multiply(model,rotT)

	projection = matrix44.create_orthogonal_projection(-2.0, 2.0, -2.0, 2.0, 2.0, -2.0)
	
	
	# atribui uma variavel uniforme para matriz de transformacao
	uMat = glGetUniformLocation(shaderProgram, "model")
	idProj = glGetUniformLocation(shaderProgram, "projection")

	

	# Note that this is allowed, the call to glVertexAttribPointer registered VBO
	# as the currently bound vertex buffer object so afterwards we can safely unbind
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	# Unbind VAO (it's always a good thing to unbind any buffer/array to prevent strange bugs)
	glBindVertexArray(0)

def drawAxis():
	global shaderProgram
	global vao
	global vbo
	global model
	global uMat
	
	


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

	

	# Note that this is allowed, the call to glVertexAttribPointer registered VBO
	# as the currently bound vertex buffer object so afterwards we can safely unbind
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	# Unbind VAO (it's always a good thing to unbind any buffer/array to prevent strange bugs)
	glBindVertexArray(0)

def draw(lista_obj,axis):
	global shaderProgram
	global vao

	for i in lista_obj: #varre a lista de objetos
		if(i.shape == 'cube'):
			init(i.shape) #manda o .obj que vai ser carregado
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			glUniformMatrix4fv(uMat, 1, GL_FALSE, model)
			Color = glGetUniformLocation(shaderProgram,"uColor")
			print('oi')
			print(i.cor)
			glUniform3f(Color,float(i.cor[0]), float(i.cor[1]) , float(i.cor[2])) # atribuindo a cor 
			if(i.wireMode == 1):
				glDrawArrays(GL_LINE_LOOP, 0, 42)
			else:
				glDrawArrays(GL_TRIANGLES, 0, 42) #desenhando o cubo

		elif(i.shape == 'torus'):
			init(i.shape) 
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			glUniformMatrix4fv(uMat, 1, GL_FALSE, model)
			glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)
			Color = glGetUniformLocation(shaderProgram,"uColor")
			glUniform3f(Color,float(i.cor[0]), float(i.cor[1]) , float(i.cor[2])) # atribuindo a cor 
			if(i.wireMode == 1):
				glDrawArrays(GL_LINES, 0, 3462)
			else:
				glDrawArrays(GL_TRIANGLES, 0, 3462) 

		elif(i.shape == 'cone'):
			init(i.shape) 
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			glUniformMatrix4fv(uMat, 1, GL_FALSE, model)
			glUniformMatrix4fv(idProj, 1, GL_FALSE, projection)
			Color = glGetUniformLocation(shaderProgram,"uColor")
			print('oi')
			print(i.cor)
			glUniform3f(Color,float(i.cor[0]), float(i.cor[1]) , float(i.cor[2])) # atribuindo a cor	
			if(i.wireMode == 1 ): 
				glDrawArrays(GL_LINES, 0, 276)
			else:
				glDrawArrays(GL_TRIANGLES, 0, 276)
				


		elif(i.shape == 'sphere'):
			init(i.shape) 
			glUseProgram(shaderProgram)
			glBindVertexArray(vao)
			glBindBuffer(GL_ARRAY_BUFFER, vbo)
			glUniformMatrix4fv(uMat, 1, GL_FALSE, model)
			Color = glGetUniformLocation(shaderProgram,"uColor")
			glUniform3f(Color,float(i.cor[0]), float(i.cor[1]) , float(i.cor[2])) # atribuindo a cor 
			if(i.wireMode == 1):
				glDrawArrays(GL_LINES, 0, 15363)
			else:
				glDrawArrays(GL_TRIANGLES, 0, 15363)

	if(axis == 1):
		drawAxis()
		glUseProgram(shaderProgram)
		glBindVertexArray(vao)
		glBindBuffer(GL_ARRAY_BUFFER, vbo)
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


#classe para armazenar os objetos
class objeto(object):
	shape = ""
	nome = ""
	cor = ""
	model = 0
	wireMode = 0

	def __init__(self, shape, nome, cor, model, wireMode):
		self.shape = shape
		self.nome = nome
		self.cor = cor
		self.model = model
		self.wireMode = wireMode

	def nome(self):
		return self.nome

	def shape(self):
		return self.shape

	def cor(self):
		return self.cor

	def model(self):
		return self.model

	def wireMode(self):
		return self.wireMode




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
	global wireMode
	glEnable(GL_DEPTH_TEST);
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	
	# load everthing back
	i = 0
	vet_obj = []
	vet_cor = [1,1,1]
	lista_obj = []

	
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
			aux = objeto(vet_obj[i+1],vet_obj[i+2],colorDefault,modelDefault,wireMode)
			lista_obj.append(aux) #cria o objeto a ser desenhado
			i = i+3 #pula para o proximo comando
			
		elif(vet_obj[i] == 'color'): #verifica se existe o comando color
			aux=i+1
			vet_cor.pop()#tira a cor padrao branca da lista
			vet_cor.pop()
			vet_cor.pop()
			print(len(vet_cor))
			for j in lista_obj:
				print(j.nome)
				if j.nome == vet_obj[aux]: #verifica se o nome passado pelo color e mesmo do objeto
					vet_cor.append(vet_obj[i+2])# coloca na lista a nova cor que foi passada
					vet_cor.append(vet_obj[i+3])
					vet_cor.append(vet_obj[i+4])
					j.cor = vet_cor #adiciona o RGB da nova cor para o campo cor no objeto
					 #pula para o proximo comando
	

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


	draw(lista_obj,vet_axis) #chama a funcao que desenha
		
		#clean things up
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	glBindVertexArray(0)
	glUseProgram(0)
	
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


