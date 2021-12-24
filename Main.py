import pygame
import time
import math
pygame.init()

square=40

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

gameBoard = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
    [0,2,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,8,1,0,],
    [0,1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,],
    [0,1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,],
    [0,1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,],
    [0,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,0,],
    [0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0,0,0,],
    [0,0,0,0,0,1,0,1,1,1,1,1,1,0,1,0,0,0,0,0,],
    [0,0,0,0,0,1,0,1,0,2,2,0,1,0,1,0,0,0,0,0,],
    [0,0,0,0,0,1,0,1,0,7,7,0,1,0,1,0,0,0,0,0,],
    [0,0,0,0,0,1,1,1,0,7,7,0,1,1,1,0,0,0,0,0,],
    [0,0,0,0,0,1,0,1,0,2,2,0,1,0,1,0,0,0,0,0,],
    [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,],
    [0,0,0,0,0,1,0,1,0,0,0,0,1,0,1,0,0,0,0,0,],
    [0,1,8,1,1,1,0,1,1,0,0,1,1,0,1,1,1,1,1,0,],
    [0,1,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,1,0,],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,8,0,],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]
]
[length,width] =[len(gameBoard[0])*square,len(gameBoard[1])*square]
screen = pygame.display.set_mode((width, length))
pygame.display.flip()
pacman=[1,1]
lives=1


def canMove(row,col):
    if gameBoard[int(row)][int(col)]!=0:
        return True
    return False


def move(direction,pacman):
    if direction == 'up':
        if canMove(math.floor(pacman[0] - .25), pacman[1]) and pacman[1] % 1.0 == 0:
            pacman[0] -= .25
    if direction == 'right':
        if canMove(pacman[0], math.ceil(pacman[1] + .25)) and pacman[0] % 1.0 == 0:
            pacman[1] += .25
    if direction == 'left':
        if canMove(pacman[0], math.floor(pacman[1] - .25)) and pacman[0] % 1.0 == 0:
            pacman[1] -= .25
    if direction == 'down':
        if canMove(math.ceil(pacman[0] + .25), pacman[1]) and pacman[1] % 1.0 == 0:
            pacman[0] += .25

def Board():
    screen.fill((0,0,0))
    for i in range(len(gameBoard[0])):
        for j in range(len(gameBoard[1])):
            if gameBoard[i][j]== 0:
                pygame.draw.rect(screen,[0,0,50],(j*square, i*square,square,square))
            elif gameBoard[i][j] == 1:
                pygame.draw.circle(screen, [255, 255, 255], (j * square + square/2, i * square + square/2), square/8)
            if gameBoard[i][j]==2:
                pygame.draw.circle(screen, [0, 0, 0], (j * square + square / 2, i * square + square / 2), square / 5)
            elif gameBoard[i][j] == 7:
                pygame.draw.circle(screen, [100,0,150], (j * square + square/2, i * square + square/2),square/4)
            elif gameBoard[i][j] == 8:
                pygame.draw.circle(screen, [204, 102, 0], (j * square + square/2, i * square + square/2),square/5)
    pygame.draw.circle(screen,[255,255,0],(math.floor(pacman[1]*square)+square/2,math.floor(pacman[0]*square+square/2)),square/3)
    pygame.display.update()

direction ='up'
running=True
coinCount=0
req='up'

while running:
    Board()
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_UP:
                req='up'
            elif event.key == K_RIGHT:
                req='right'
            elif event.key == K_LEFT:
                req='left'
            elif event.key == K_DOWN:
                req='down'

    if req=='up':
        if (canMove(math.floor(pacman[0] - .25), pacman[1]) and pacman[1]%1.0 ==0):
            direction='up'
        move(direction,pacman)
    if req=='right':
        if (canMove(pacman[0], math.ceil(pacman[1] + .25)) and pacman[0]%1.0 ==0):
            direction='right'
        move(direction, pacman)
    if req=='left':
        if (canMove(pacman[0], math.floor(pacman[1] - .25)) and pacman[0]%1.0 ==0):
            direction='left'
        move(direction,pacman)
    if req=='down':
        if (canMove(math.ceil(pacman[0] + .25), pacman[1]) and pacman[1]%1.0 ==0):
            direction='down'
        move(direction, pacman)

    if gameBoard[int(pacman[0])][int(pacman[1])] == 1:
        coinCount += 10
        print("The current coins:", coinCount)
        gameBoard[int(pacman[0])][int(pacman[1])] = 2
    if gameBoard[int(pacman[0])][int(pacman[1])] == 8:
        coinCount+= 200
        print("The current coins:", coinCount)
        gameBoard[int(pacman[0])][int(pacman[1])] = 2

    time.sleep(0.035)
