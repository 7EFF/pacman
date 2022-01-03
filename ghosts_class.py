import pygame,sys,os
import time
import math
from math import radians
from pygame import mixer
from pygame.locals import *
pygame.init()
pygame.font.init()
pygame.mixer.init()

class Ghost:
    def __init__(self,main,pos,gh_colour):
        self.main=main
        self.pos=pos
        self.gh_colour=gh_colour
    def updateGhost(self):
        pass
    def drawGhost(self):
        pygame.draw.circle(self.main.screen, self.gh_colour, (self.pos[1]* self.main.square + self.main.square/2,self.pos[0]* self.main.square + self.main.square/2),self.main.square / 4)
        pygame.display.update()