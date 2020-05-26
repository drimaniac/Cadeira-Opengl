import math

import numpy as np
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import keyboard

def loadTexture(image_file):
    textureSurface = pygame.image.load(image_file)
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
    width = textureSurface.get_width()
    height = textureSurface.get_height()

    glEnable(GL_TEXTURE_2D)
    texid = glGenTextures(1, image_file)
    glBindTexture(GL_TEXTURE_2D, texid)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    return texid

verticies = (
    ( 1, -1, -1), #0
    ( 1,  1, -1), #1
    (-1,  1, -1), #2
    (-1, -1, -1), #3
    ( 1, -1,  1), #4
    ( 1,  1,  1), #5
    (-1, -1,  1), #6
    (-1,  1,  1)  #7
    )

normals = (
    (0, 0, -1),
    (0, 0, 1),
    (0, -1, 0),
    (0, 1, 0),
    (-1, 0, 0),
    (1, 0, 0),
)

faces = (
    (0, 1, 2, 3),
    (4, 5, 7, 6),
    (0, 3, 6, 4),
    (1, 2, 7, 5),
    (2, 3, 6, 7),
    (0, 1, 5, 4)
    )

#Função responável pela criação dos cubos
def Cubo(wireframe, texture = None):
    if not texture is None:
        glBindTexture(GL_TEXTURE_2D, texture)

    if wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

    glBegin(GL_QUADS)
    texIndexes = [(1,0), (1,1), (0, 1), (0,0)]
    for face, normal in zip(faces, normals):
        glNormal3d(normal[0], normal[1], normal[2] )
        for vertex, texIndex in zip(face, texIndexes):
            if not texture is None:
                glTexCoord2f(texIndex[0], texIndex[1])
            glVertex3fv(verticies[vertex])
    glEnd()


# right = true or false
def move_target(eye, target, right):
    # translada a câmera para a origem
    t0 = target - eye

    # Ignora a componente Y
    t0[1] = 0

    # Calcula o raio do círculo
    r = math.sqrt(t0[0] * t0[0] + t0[2] * t0[2])

    # Calcula o seno e o cosseno e a tangente do ângulo que o vetor faz com o eixo X
    sin_alfa = t0[2] / r
    cos_alfa = t0[0] / r
    if cos_alfa == 0:
        if sin_alfa == 1:
            alfa = math.pi / 2
        else:
            alfa = - math.pi / 2
    else:
        tg_alfa = sin_alfa / cos_alfa

        # Calcula o arco cuja tangente é calculada no passo anterior
        alfa = np.arctan(tg_alfa)

        # Como o retorno de arctan varia somente entre -pi/2 e pi/2, testar o cosseno para
        # calcular o ângulo correto
        if cos_alfa < 0:
            alfa = alfa - math.pi

    if right:
        signal = 1
    else:
        signal = -1

    # Varia o ângulo do alvo (target)
    alfa = alfa + 0.1 * signal

    # Calcula o novo alvo (sobre o eixo Y)
    t0[0] = r * math.cos(alfa)
    t0[2] = r * math.sin(alfa)

    n_target = eye + t0

    return n_target


# ahead = true or false
def move_can(eye, target, ahead):
    # equação paramétrica
    a = np.zeros(3)
    delta = 0.1
    p0 = eye
    p1 = target
    a = p1 - p0
    print('------------------------')
    print(p1)
    print(p0)
    print(a)

    if ahead:
        signal = 1
    else:
        signal = -1
    p0 = p0 + delta * a * signal
    # p1 = p1 + delta * a * signal

    # Câmera sobre o plano (X, Z)
    # p0[1] = 0

    return p0, p1

def main():
    # Translação do cubo verde
    tx = 0
    ty = 0

    # Item E: Dados para rotacionar a câmera
    radiano = 10
    angle = 3.1415 / 2

    # UP vector angle = Pi/2 (90o)
    up_angle = 3.1415 / 2

    rot_angle = 3.1415 / 2

    wireframe = False

    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    gluPerspective(45, (display[0] / display[1]), 0.1, 80.0)

    #Item C: Posicionamento da câmera no ponto (0, 8, 30)
    eye = np.zeros(3)
    eye[1] = 8
    eye[2] = 30

    #Item C: Colocando como alvo de observaç~çao o ponto (0, 0, 0)
    target = np.zeros(3)

    #Item C: Coloca o Up vector apontado para o eixo Y
    up = np.zeros(3)
    up[1] = 1

    t_quad = loadTexture('textura_cadeira.jpeg')
    while True:
        # print(eye)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                # Movimentação do cubo
                if event.key == K_w:
                    ty = ty + 0.5
                elif event.key == K_s:
                    ty = ty - 0.5
                elif event.key == K_a:
                    tx = tx + 0.5
                elif event.key == K_d:
                    tx = tx - 0.5

                # Movimentação da direção da câmera
                # nos eixos X e Y (olho)
                elif event.key == K_UP:
                    target[1] = target[1] + 0.5
                elif event.key == K_DOWN:
                    target[1] = target[1] - 0.5
                # move_target(eye, target, right):
                elif event.key == K_RIGHT:
                    target = move_target(eye, target, True)
                elif event.key == K_LEFT:
                    target = move_target(eye, target, False)

                elif event.key == K_PAGEUP:
                    # Mover para frente
                    eye, target = move_can(eye, target, True)
                    # eye[2] = eye[2] - 0.5
                elif event.key == K_PAGEDOWN:
                    # Mover para trás
                    eye, target = move_can(eye, target, False)
                    # eye[2] = eye[2] + 0.5

                elif event.key == K_t:
                    eye[0] = eye[0] - 0.5
                elif event.key == K_g:
                    eye[0] = eye[0] + 0.5

                # Movimentação da parte de cima da câmera (UP vector)
                elif event.key == K_PERIOD:
                    up_angle += 0.05
                    up[1] = math.sin(up_angle)
                    up[0] = math.cos(up_angle)
                elif event.key == K_COMMA:
                    up_angle -= 0.05
                    up[1] = math.sin(up_angle)
                    up[0] = math.cos(up_angle)

                # Wireframe
                elif event.key == K_SPACE:
                    wireframe = not wireframe

                #Girar camera
                elif event.key == K_i:
                    angle += 0.5
                    eye[0] = math.sin(angle) * radiano
                    eye[2] = math.cos(angle) * radiano
                elif event.key == K_o:
                    angle -= 0.5
                    eye[0] = math.sin(angle) * radiano
                    eye[2] = math.cos(angle) * radiano

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # eye_dist = math.sqrt(eye[0]*eye[0] + eye[1]*eye[1] +eye[2]*eye[2])
                eye_dist = math.sqrt(eye[0] * eye[0] + eye[2] * eye[2])
                # print(eye, eye_dist)
                if event.button == 4:
                    rot_angle += 0.02
                    eye[2] = eye_dist * math.sin(rot_angle)
                    eye[0] = eye_dist * math.cos(rot_angle)

                if event.button == 5:
                    rot_angle -= 0.02
                    eye[2] = eye_dist * math.sin(rot_angle)
                    eye[0] = eye_dist * math.cos(rot_angle)
                    # Item E: Rotacionar câmera no eixo Y

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #Item A.3: Habilitar teste de profundidade
        glEnable(GL_DEPTH_TEST)
        glPushMatrix()
        gluLookAt(eye[0], eye[1], eye[2],
                  target[0], target[1], target[2],
                  up[0], up[1], up[2])

        #Item A.1 e A.2: Criação do caractere
        texture = True
        glPushMatrix()
        glRotatef(180, 0, 1, 0)  # rotacionar para ficar de frente para a câmera


        glPushMatrix()
        glTranslatef(tx, ty, 0.)
        glScalef(3, 0.4, 3)
        Cubo(wireframe, texture= t_quad)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(tx, ty, 0.)
        glTranslatef(2.4, -3.2, 2.4)
        glScalef(0.4, 2.8, 0.4)
        Cubo(wireframe, texture= t_quad)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(tx, ty, 0.)
        glTranslatef(2.4, -3.2, -2.4)
        glScalef(0.4, 2.8, 0.4)
        Cubo(wireframe, texture= t_quad)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(tx, ty, 0.)
        glTranslatef(-2.4, -3.2, 2.4)
        glScalef(0.4, 2.8, 0.4)
        Cubo(wireframe, texture= t_quad)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(tx, ty, 0.)
        glTranslatef(-2.4, -3.2, -2.4)
        glScalef(0.4, 2.8, 0.4)
        Cubo(wireframe, texture= t_quad)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(tx, ty, 0.)
        glTranslatef(0, 3.5, 2.2)
        glScalef(2.8, 3.5, 0.4)
        Cubo(wireframe, texture=t_quad)
        glPopMatrix()

        glPopMatrix()
        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

main()