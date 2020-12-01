import sys
import numpy as np
import math 
import pywavefront as obj
import pyrr 
import re
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *

vao = None
vbo = None
shaderProgram = None
uMat = None            # variavel uniforme
model = None        # matriz de transformação
rotate = 0

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

def init():
	global shaderProgram
	global vao
	global vbo
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
	vertices = np.array(readVertexData(), dtype='f')
	print("vertices:", len(vertices)//6)
	print(vertices)

	
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
	scale = pyrr.matrix44.create_from_scale([0.5,0.5,0.5],dtype='f')
	model = pyrr.matrix44.multiply(model,scale)


	rotZ = pyrr.matrix44.create_from_z_rotation(math.radians(0))
	rotY = pyrr.matrix44.create_from_y_rotation(math.radians(45))
	rotx = pyrr.matrix44.create_from_x_rotation(math.radians(45))
	rotT = pyrr.matrix44.multiply(rotY,rotx)
	rotT = pyrr.matrix44.multiply(rotT,rotZ)

	model = pyrr.matrix44.multiply(model,rotT)
	
	
	# atribui uma variavel uniforme para matriz de transformacao
	uMat = glGetUniformLocation(shaderProgram, "model")

	

	# Note that this is allowed, the call to glVertexAttribPointer registered VBO
	# as the currently bound vertex buffer object so afterwards we can safely unbind
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	# Unbind VAO (it's always a good thing to unbind any buffer/array to prevent strange bugs)
	glBindVertexArray(0)


def draw():
	global shaderProgram
	global vao
	init()
	glUseProgram(shaderProgram)
	glBindVertexArray(vao)
	glBindBuffer(GL_ARRAY_BUFFER, vbo)
	glUniformMatrix4fv(uMat, 1, GL_FALSE, model)
	glDrawArrays(GL_TRIANGLES, 0, 4000)

def display():
	
	
	
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	
	# load everthing back
	
	vet_obj = []
	#glDrawArrays( mode , first, count)
	#glDrawArrays(GL_LINES, 0, 36)
	arq = sys.argv[1]

	arquivo = open(arq,'r')
	for linha in arquivo:
		linha = linha.replace('\n','')
		if('add_shape' in linha):
			for i in linha.split():
				if(i == 'cube'):
					shape = i
					draw()
					
				
		print(linha)
		#clean things up
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	glBindVertexArray(0)
	glUseProgram(0)
	
	glutSwapBuffers()  # necessario para windows!

	
	
	
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
