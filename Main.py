import pygame,sys,os
import time
import math
from math import radians
from pygame import mixer
from pygame.locals import *
pygame.init()
pygame.font.init()
pygame.mixer.init()
from ghosts_class import *

class PacMan:
    def __init__(self,direction,gameBoard,square,screen,pacman,coinCount,length,width,pacspeed,eatGhosts):
        self.direction=direction
        self.gameBoard = gameBoard
        self.square=square
        self.screen=screen
        self.pacman=pacman
        self.coinCount=coinCount
        self.length=length
        self.width=width
        self.pacspeed=pacspeed
        self.ghosts = []
        self.eatGhosts=eatGhosts

    ###########################SET & GET###########################

    def setDirection(self,direction):
        self.direction=direction

    def setPacMan(self,pacman):
        self.pacman=pacman

    def setCoinCount(self,coinCount):
        self.coinCount=coinCount

    def setEatGhosts(self,eatGhost):
        self.eatGhosts=eatGhost

    ###########################SET & GET###########################


    ###########################MOVEMENT###########################

    def canMove(self,row,col):
        if self.gameBoard[int(row)][int(col)]!=0:
            return True
        return False


    def move(self,direction,row,col):
        if direction == 'up':
            if self.canMove(math.floor(row - self.pacspeed), col) and col % 1.0 == 0:
                row -= self.pacspeed
        elif direction == 'right':
            if self.canMove(row, math.ceil(col + self.pacspeed)) and row % 1.0 == 0:
                col += self.pacspeed
        elif direction == 'left':
            if self.canMove(row, math.floor(col - self.pacspeed)) and row % 1.0 == 0:
                col -= self.pacspeed
        else:
            if self.canMove(math.ceil(row + self.pacspeed), col) and col % 1.0 == 0:
                row += self.pacspeed
        return row,col

    ###########################MOVEMENT###########################

    ###########################GHOSTS###########################

    def fruitEaten(self):
        for gh in self.ghosts:
            gh.drawGhost()
            gh.fruitEaten()
        pygame.display.update()

    def draw_Ghosts(self):
        for gh in self.ghosts:
            gh.drawGhost()
            gh.movementBehaves()
        pygame.display.update()

    def make_Ghosts(self):
        self.ghosts = [Ghost(self, 11, 10, [0, 255, 0],self.pacman[0],self.pacman[1]), Ghost(self, 10, 10, [255, 150, 0],self.pacman[0],self.pacman[1]),Ghost(self, 11, 9, [255, 0, 0],self.pacman[0],self.pacman[1]), Ghost(self, 10, 9, [100, 0, 150],self.pacman[0],self.pacman[1])]
        for gh in self.ghosts:
            gh.drawGhost()
        pygame.display.update()

    ###########################GHOSTS###########################

    ###########################DRAWING###########################

    def Board(self):
        self.screen.fill((0,0,0))
        for i in range(len(self.gameBoard[0])):
            for j in range(len(self.gameBoard[1])):
                if self.gameBoard[i][j]== 0:
                    pygame.draw.rect(self.screen,[0, 0, 77],(j*self.square, i*self.square,self.square,self.square),math.floor(self.square/2))
                    pygame.draw.rect(self.screen, [100, 100, 180],(j * self.square, i * self.square, int(self.square/1.5), int(self.square/1.5)))
                elif self.gameBoard[i][j] == 1:
                    pygame.draw.circle(self.screen, [255, 255, 255], (j * self.square + self.square/2, i * self.square + self.square/2), self.square/15)
                elif self.gameBoard[i][j]==2:
                    pygame.draw.circle(self.screen, [0, 0, 0], (j * self.square + self.square / 2, i * self.square + self.square / 2), self.square / 5)
                elif self.gameBoard[i][j] == 3:
                    pygame.draw.circle(self.screen, [204, 102, 0], (j * self.square + self.square/2, i * self.square + self.square/2),self.square/5)
                else:
                    self.g_pos.append([i, j])
        pygame.draw.circle(self.screen,[255,255,0],(math.floor(self.pacman[1]*self.square+self.square/2),math.floor(self.pacman[0]*self.square+self.square/2)),self.square/3)
        Font = pygame.font.SysFont('arial black', math.floor(self.square/1.5))
        text = Font.render('COINS: {}'.format(self.coinCount), True, (255, 255, 0))
        textRect = text.get_rect()
        textRect.center = (self.length / 2, self.width / 20)
        self.screen.blit(text, textRect)
        pygame.display.update()

    def winning(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            self.screen.fill((0, 0, 0))
            Font = pygame.font.SysFont('arial black', 30)
            text = Font.render('YOU WON THIS DUEL', True, (255, 255, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2, self.width / 3)
            self.screen.blit(text, textRect)
            pygame.display.update()

    def Intro_Render(self):
        running = True
        while running:
            self.screen.fill((0, 0, 0))
            Font = pygame.font.SysFont('arial black', 30)
            text = Font.render('PRESS SPACE TO START', True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2, self.width / 5)
            self.screen.blit(text, textRect)
            if self.square>=35:
                player = pygame.image.load(os.path.join("pacman_pic.png"))
                self.screen.blit(player, (self.length/5, self.width/3))
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_SPACE:
                        intro_sound = mixer.Sound('pacman_beginning.wav')
                        intro_sound.set_volume(0.2)
                        intro_sound.play()
                        for i in range(len(self.gameBoard[0])):
                            for j in range(len(self.gameBoard[1])):
                                pygame.draw.rect(self.screen, [0, 0, 77],(j * self.square, i * self.square, self.square, self.square))
                                pygame.draw.rect(self.screen, [100, 100, 180], (j * self.square, i * self.square, int(self.square / 1.5), int(self.square / 1.5)))
                            time.sleep(4/len(self.gameBoard[0]))
                            if i==len(self.gameBoard[0]):
                                break
                            pygame.display.update()
                        return
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    def died_wait(self):
        fruit_Sound = mixer.Sound('pacman_death.wav')
        fruit_Sound.set_volume(0.2)
        fruit_Sound.play()
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            self.screen.fill((0, 0, 0))
            Font = pygame.font.SysFont('arial black', 30)
            text = Font.render('YOU DIED, WAITING FOR OPPONENT', True, (255, 255, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2, self.width / 2)
            self.screen.blit(text, textRect)
            pygame.display.update()

    ###########################DRAWING###########################

def main():

    square = 35
    pacspeed=1/16
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
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 3, 1, 0, ],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, ],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, ],
        [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 1, 1, 2, 2, 1, 1, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 1, 1, 0, 2, 2, 0, 1, 1, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 2, 2, 0, 1, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 2, 2, 0, 1, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 1, 3, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, ],
        [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]
        #1=מקום עם מטבעות
        #0=קיר שאי אפשר לעבור
        #2=מקום שאפשר ללכת בוא אבל בלי מטבעות
        #3=מטסעות גדולים
    ]
    print (len(gameBoard[0])," width")
    print (len(gameBoard[1]), " length")
    [length, width] = [len(gameBoard[0]) * square, len(gameBoard[1]) * square]
    screen = pygame.display.set_mode((width, length))
    pygame.display.flip()
    pacman = [1, 1]
    pygame.display.set_caption("PacMan-Final Project")
    direction = 'up'
    running = True
    coinCount = 0
    req = 'up'
    blueCounter=0
    eatGhosts=False
    user = PacMan(direction, gameBoard, square, screen, pacman,coinCount,length,width,pacspeed,eatGhosts)
    user.Intro_Render()
    user.make_Ghosts()
    while running:
        user.Board()
        user.draw_Ghosts()
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
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        if req=='up':
            if (user.canMove(math.floor(pacman[0] - pacspeed), pacman[1]) and pacman[1]%1.0 ==0):
                direction='up'
        if req=='right':
            if (user.canMove(pacman[0], math.ceil(pacman[1] + pacspeed)) and pacman[0]%1.0 ==0):
                direction='right'
        if req=='left':
            if (user.canMove(pacman[0], math.floor(pacman[1] - pacspeed)) and pacman[0]%1.0 ==0):
                direction='left'
        if req=='down':
            if (user.canMove(math.ceil(pacman[0] + pacspeed), pacman[1]) and pacman[1]%1.0 ==0):
                direction='down'
        pacman[0], pacman[1] = user.move(direction, pacman[0], pacman[1])
        if gameBoard[int(pacman[0])][int(pacman[1])] == 1:
            coinCount += 10
            print("The current coins:", coinCount)
            gameBoard[int(pacman[0])][int(pacman[1])] = 2
            if pygame.mixer.get_busy()==False:
                eating_Sound= mixer.Sound('pacman_chomp.wav')
                eating_Sound.set_volume(0.2)
                eating_Sound.play()
        if gameBoard[int(pacman[0])][int(pacman[1])] == 3:
            coinCount+= 200
            print("The current coins:", coinCount)
            gameBoard[int(pacman[0])][int(pacman[1])] = 2
            fruit_Sound = mixer.Sound('pacman_eatfruit.wav')
            fruit_Sound.set_volume(0.25)
            fruit_Sound.play()
            user.fruitEaten()
            eatGhosts=True
            blueCounter=0
        for gh in user.ghosts:
            died = gh.ifTouched()
            if died=='died':
                user.died_wait()
            if died=='eaten':
                gh.eatenBlue()
                coinCount+=400
                print("The current coins:", coinCount)
                eat_ghost = mixer.Sound('pacman_eatghost.wav')
                eat_ghost.set_volume(0.3)
                eat_ghost.play()
        if eatGhosts:
            if blueCounter==900:
                for gh in user.ghosts:
                    gh.blueOver()
                blueCounter=0
                eatGhosts=False
            if blueCounter >= 700 and blueCounter % 40 == 0:
                for gh in user.ghosts:
                    if gh.getDied()==False:
                        gh.flickerToBLUE()
            if blueCounter >= 700 and blueCounter % 40 == 20:
                for gh in user.ghosts:
                    gh.flickerToOG()
            blueCounter+=1
        if coinCount>4000:
            user.winning()
        user.setPacMan(pacman)
        user.setCoinCount(coinCount)
        user.setDirection(direction)
        user.setEatGhosts(eatGhosts)
if __name__ == '__main__':
    main()
