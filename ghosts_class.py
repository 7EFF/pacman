import pygame,sys,os
import time
import math
from math import radians
from pygame import mixer
from pygame.locals import *
import random
pygame.init()
pygame.font.init()
pygame.mixer.init()

class Ghost:
    def __init__(self,main,row,col,colour,pacmanRow,pacmanCol):
        self.main=main
        self.row=row
        self.col=col
        self.colour=colour
        self.pacmanRow = pacmanRow
        self.pacmanCol=pacmanCol
        self.ghostspeed=1/32
        self.ghostBehave='Random'
        self.direction='down'

    def ifTouched(self):
        if int(self.row)==int(self.main.pacman[0]) and int(self.main.pacman[1])==int(self.col):
            return True

    def canMove(self,row,col):
        if self.main.gameBoard[int(row)][int(col)]!=0:
            return True
        return False

    def randDirection(self):
        if self.canMove(math.ceil(self.row + self.ghostspeed), self.col) and self.col % 1.0 == 0:
            self.direction = 'down'
        if self.canMove(self.row, math.ceil(self.col + self.ghostspeed)) and self.row % 1.0 == 0:
            self.direction='right'
        if self.canMove(self.row, math.floor(self.col - self.ghostspeed)) and self.row % 1.0 == 0:
            self.direction='left'
        if self.canMove(math.floor(self.row - self.ghostspeed), self.col) and self.col % 1.0 == 0:
            self.direction='up'
        self.move()


    def movementBehaves(self):
        if self.ghostBehave=='Random':
            self.randDirection()

    def move(self):
        if self.direction == 'up':
            self.row -= self.ghostspeed
        if self.direction == 'right':
            self.col += self.ghostspeed
        if self.direction == 'left':
            self. col -= self.ghostspeed
        if self.direction == 'down':
            self. row += self.ghostspeed
        pygame.display.update()

    def drawGhost(self):
        pygame.draw.circle(self.main.screen, self.colour, (math.floor(self.col* self.main.square + self.main.square/2),math.floor(self.row* self.main.square + self.main.square/2)),self.main.square / 4)
