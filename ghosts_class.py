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
        self.ghostBehave='Leave'
        self.direction='up'
        self.died=False
        self.leftSpawn=False

    def ifTouched(self):
        if math.floor(self.row)==math.floor(self.main.pacman[0]) and math.ceil(self.main.pacman[1])==math.ceil(self.col) and self.main.eatGhosts==False:
            return 'died'
        if math.floor(self.row)==math.floor(self.main.pacman[0]) and math.ceil(self.main.pacman[1])==math.ceil(self.col) and self.main.eatGhosts==True and self.died==False:
            return 'eaten'
        if math.floor(self.row) == math.floor(self.main.pacman[0]) and math.ceil(self.main.pacman[1]) == math.ceil(self.col) and self.died==True:
            return 'died'

    def canMove(self,row,col,index):
        if self.main.gameBoard[int(row)][int(col)]!=index and self.main.gameBoard[int(row)][int(col)]!=0:
            return True
        return False

    def changeBehavior(self,NewBehave):
        self.ghostBehave=NewBehave

    def randDirection(self):
        index = 0
        if self.died:
            index = 4
        possibleTurn=[]
        if self.canMove(math.floor(self.row - self.ghostspeed), self.col,index) and self.col % 1.0 == 0 and self.direction!='down':
            possibleTurn.append('up')
        if self.canMove(self.row, math.ceil(self.col + self.ghostspeed),index) and self.row % 1.0 == 0 and self.direction!='left':
            possibleTurn.append('right')
        if self.canMove(self.row, math.floor(self.col - self.ghostspeed),index) and self.row % 1.0 == 0 and self.direction!='right':
            possibleTurn.append('left')
        if self.canMove(math.ceil(self.row + self.ghostspeed), self.col,index) and self.col % 1.0 == 0 and self.direction!='up':
            possibleTurn.append('down')
        if len(possibleTurn)>=1:
            self.direction=random.choice(possibleTurn)
        self.move()

    def movementBehaves(self):
        if self.ghostBehave=='Random':
            self.randDirection()
            print(self.colour,'Random')
        if self.ghostBehave=='Leave':
            print(self.colour,' Leave')
            self.move()
            if self.main.gameBoard[int(self.row)][int(self.col)]==5:
                self.leftSpawn=True
                self.changeBehavior('Random')

    def move(self):
        index =0
        if self.died or self.leftSpawn:
            index=4
        if self.direction == 'up':
            if self.canMove(math.floor(self.row - self.ghostspeed), self.col,index) and self.col % 1.0 == 0:
                self.row -= self.ghostspeed
        elif self.direction == 'right':
            if self.canMove(self.row, math.ceil(self.col + self.ghostspeed),index) and self.row % 1.0 == 0:
                self.col += self.ghostspeed
        elif self.direction == 'left':
            if self.canMove(self.row, math.floor(self.col - self.ghostspeed),index) and self.row % 1.0 == 0:
                self. col -= self.ghostspeed
        elif self.direction == 'down':
            if self.canMove(math.ceil(self.row + self.ghostspeed), self.col,index) and self.col % 1.0 == 0:
                self. row += self.ghostspeed
        if self.col<0.015625 and self.direction=='left':
            self.col = 27.484375
        if self.col>26.984375 and self.direction=='right':
            self.col = 0.015625
        print (self.row)
        return

    def getColour(self):
        return self.colour

    def bigCoinEaten(self):
        self.colour = 'blue'
        self.movementBehaves()
        self.ghostspeed=1/256
        self.died=False

    def eatenBlue(self):
        self.row = self.ogrow
        self.col = self.ogcol
        self.colour = self.ogcolour
        self.ghostspeed = 1 / 128
        self.died=True
        self.leftSpawn = False
        self.direction='up'

    def flickerToOG(self):
        self.colour = self.ogcolour

    def flickerToBLUE(self):
        self.colour = 'blue'

    def getDied(self):
        return self.died

    def blueOver(self):
        self.colour = self.ogcolour
        self.ghostspeed = 1 / 128
        self.died=False
        if self.leftSpawn==False:
            self.direction='up'
            self.ghostBehave='Leave'
            self.movementBehaves()

    def DirForPic(self):
        if self.direction == 'up':
            return 'up.png'
        elif self.direction == 'down':
            return 'down.png'
        elif self.direction == 'right':
            return 'right.png'
        elif self.direction == 'left':
            return 'left.png'

    def drawGhost(self):
        Directory=''
        if self.colour=='blue':
            Directory = 'GhostsPics\_blue.png'
        else:
            if self.colour=='pink':
                Directory='GhostsPics\_pink_'
                Dir=self.DirForPic()
                Directory = Directory+Dir
            elif self.colour=='cyan':
                Directory = 'GhostsPics\_cyan_'
                Dir = self.DirForPic()
                Directory = Directory + Dir
            elif self.colour=='yellow':
                Directory = 'GhostsPics\_yellow_'
                Dir = self.DirForPic()
                Directory = Directory + Dir
            elif self.colour=='red':
                Directory='GhostsPics\_red_'
                Dir = self.DirForPic()
                Directory = Directory + Dir
        ghost_Pic = pygame.image.load(Directory).convert()
        ghost_Pic = pygame.transform.scale(ghost_Pic, (int(self.main.square * 1.3), int(self.main.square * 1.3)))
        self.main.screen.blit(ghost_Pic, (math.floor(self.col * self.main.square), math.floor(self.row * self.main.square), self.main.square, self.main.square))
