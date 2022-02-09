import pygame
import math
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
        self.ogrow=row
        self.ogcol=col
        self.ogcolour = colour
        self.ghostspeed=1/128
        self.ghostBehave='Random'
        self.direction='up'
        self.died=False

    def ifTouched(self):
        if math.floor(self.row)==math.floor(self.main.pacman[0]) and math.floor(self.main.pacman[1])==math.floor(self.col) and self.main.eatGhosts==False:
            return 'died'
        if math.floor(self.row)==math.floor(self.main.pacman[0]) and math.floor(self.main.pacman[1])==math.floor(self.col) and self.main.eatGhosts==True and self.died==False:
            return 'eaten'
        if math.floor(self.row) == math.floor(self.main.pacman[0]) and math.floor(self.main.pacman[1]) == math.floor(self.col) and self.died==True:
            return 'died'

    def canMove(self,row,col):
        if self.main.gameBoard[int(row)][int(col)]!=0:
            return True
        return False

    def randDirection(self):
        possibleTurn=[]
        if self.canMove(math.floor(self.row - self.ghostspeed), self.col) and self.col % 1.0 == 0 and self.direction!='down':
            possibleTurn.append('up')
        if self.canMove(self.row, math.ceil(self.col + self.ghostspeed)) and self.row % 1.0 == 0 and self.direction!='left':
            possibleTurn.append('right')
        if self.canMove(self.row, math.floor(self.col - self.ghostspeed)) and self.row % 1.0 == 0 and self.direction!='right':
            possibleTurn.append('left')
        if self.canMove(math.ceil(self.row + self.ghostspeed), self.col) and self.col % 1.0 == 0 and self.direction!='up':
            possibleTurn.append('down')
        if len(possibleTurn)>=1:
            self.direction=random.choice(possibleTurn)
        self.move()

    def movementBehaves(self):
        if self.ghostBehave=='Random':
            self.randDirection()

    def move(self):
        if self.direction == 'up':
            if self.canMove(math.floor(self.row - self.ghostspeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.ghostspeed
        elif self.direction == 'right':
            if self.canMove(self.row, math.ceil(self.col + self.ghostspeed)) and self.row % 1.0 == 0:
                self.col += self.ghostspeed
        elif self.direction == 'left':
            if self.canMove(self.row, math.floor(self.col - self.ghostspeed)) and self.row % 1.0 == 0:
                self. col -= self.ghostspeed
        elif self.direction == 'down':
            if self.canMove(math.ceil(self.row + self.ghostspeed), self.col) and self.col % 1.0 == 0:
                self. row += self.ghostspeed

    def getColour(self):
        return self.colour

    def fruitEaten(self):
        self.colour = [0, 0, 255]
        self.movementBehaves()
        self.ghostspeed=1/256
        self.died=False

    def eatenBlue(self):
        self.row = self.ogrow
        self.col = self.ogcol
        self.colour = self.ogcolour
        self.ghostspeed = 1 / 128
        self.died=True

    def flickerToOG(self):
        self.colour = self.ogcolour

    def flickerToBLUE(self):
        self.colour = [0,0,255]

    def getDied(self):
        return self.died

    def blueOver(self):
        self.colour = self.ogcolour
        self.ghostspeed = 1 / 128

    def drawGhost(self):
        pygame.draw.circle(self.main.screen, self.colour, (math.floor(self.col* self.main.square + self.main.square/2),math.floor(self.row* self.main.square + self.main.square/2)),self.main.square / 4)
