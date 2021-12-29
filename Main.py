import pygame,sys
import time
import math
from math import radians
from pygame import mixer
from pygame.locals import *
pygame.init()
pygame.font.init()
pygame.mixer.init()
MOUTH_EVENT = USEREVENT+1

class PacMan:
    def __init__(self,direction,gameBoard,square,screen,pacman,coinCount,length,width):
        self.direction=direction
        self.gameBoard = gameBoard
        self.square=square
        self.screen=screen
        self.pacman=pacman
        self.mouth_closed=False
        self.coinCount=coinCount
        self.length=length
        self.width=width

    def canMove(self,row,col):
        if self.gameBoard[int(row)][int(col)]!=0:
            return True
        return False


    def move(self,direction,row,col):
        if direction == 'up':
            if self.canMove(math.floor(row - .25), col) and col % 1.0 == 0:
                row -= .25
        if direction == 'right':
            if self.canMove(row, math.ceil(col + .25)) and row % 1.0 == 0:
                col += .25
        if direction == 'left':
            if self.canMove(row, math.floor(col - .25)) and row % 1.0 == 0:
                col -= .25
        if direction == 'down':
            if self.canMove(math.ceil(row + .25), col) and col % 1.0 == 0:
                row += .25
        return row,col

    def Board(self):
        self.screen.fill((0,0,0))
        for i in range(len(self.gameBoard[0])):
            for j in range(len(self.gameBoard[1])):
                if self.gameBoard[i][j]== 0:
                    pygame.draw.rect(self.screen,[15,0,50],(j*self.square, i*self.square,self.square,self.square),math.floor(self.square/2))
                    pygame.draw.rect(self.screen, [15, 0, 50],(j * self.square, i * self.square, int(self.square/1.5), int(self.square/1.5)))
                elif self.gameBoard[i][j] == 1:
                    pygame.draw.circle(self.screen, [255, 255, 255], (j * self.square + self.square/2, i * self.square + self.square/2), self.square/8,int(self.square/20))
                if self.gameBoard[i][j]==2:
                    pygame.draw.circle(self.screen, [0, 0, 0], (j * self.square + self.square / 2, i * self.square + self.square / 2), self.square / 5)
                elif self.gameBoard[i][j] == 3:
                    pygame.draw.circle(self.screen, [100,0,150], (j * self.square + self.square/2, i * self.square + self.square/2),self.square/4)
                elif self.gameBoard[i][j] == 4:
                    pygame.draw.circle(self.screen, [204, 102, 0], (j * self.square + self.square/2, i * self.square + self.square/2),self.square/5)
        pygame.draw.circle(self.screen,[255,255,0],(math.floor(self.pacman[1]*self.square+self.square/2),math.floor(self.pacman[0]*self.square+self.square/2)),self.square/3)
        Font = pygame.font.SysFont('arial black', math.floor(self.square/2))
        text = Font.render('COINS: {}'.format(self.coinCount), True, (255, 255, 0))
        textRect = text.get_rect()
        textRect.center = (self.length / 2, self.width / 20)
        self.screen.blit(text, textRect)
        pygame.display.flip()
        pygame.display.update()

    def Intro_Render(self):
        running = True
        while running:
            self.screen.fill((0, 0, 0))
            Font = pygame.font.SysFont('arial black', 30)
            text = Font.render('PRESS SPACE TO START', True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2, self.width / 20)
            self.screen.blit(text, textRect)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_SPACE:
                        intro_sound = mixer.Sound('pacman_beginning.wav')
                        intro_sound.set_volume(0.2)
                        intro_sound.play()
                        time.sleep(4)
                        return
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
    def died_wait(self):
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
def main():
    square = 35

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
        [0, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 4, 1, 0, ],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, ],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, ],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 1, 1, 2, 2, 1, 1, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 1, 1, 0, 2, 2, 0, 1, 1, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 3, 3, 0, 1, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 3, 3, 0, 1, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 1, 1, 0, 2, 2, 0, 1, 1, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 1, 2, 2, 2, 2, 1, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, ],
        [0, 1, 4, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, ],
        [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]
    ]
    [length, width] = [len(gameBoard[0]) * square, len(gameBoard[1]) * square]
    screen = pygame.display.set_mode((width, length))
    pygame.display.flip()
    pacman = [1, 1]
    lives = 1
    pygame.display.set_caption("PacMan-Final Project")
    direction = 'up'
    running = True
    coinCount = 0
    req = 'up'
    user = PacMan(direction, gameBoard, square, screen, pacman,coinCount,length,width)
    user.Intro_Render()
    while running:
        user.Board()
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
            if (user.canMove(math.floor(pacman[0] - .25), pacman[1]) and pacman[1]%1.0 ==0):
                direction='up'
            pacman[0],pacman[1]=user.move(direction, pacman[0],pacman[1])
        if req=='right':
            if (user.canMove(pacman[0], math.ceil(pacman[1] + .25)) and pacman[0]%1.0 ==0):
                direction='right'
            pacman[0],pacman[1]=user.move(direction, pacman[0],pacman[1])
        if req=='left':
            if (user.canMove(pacman[0], math.floor(pacman[1] - .25)) and pacman[0]%1.0 ==0):
                direction='left'
            pacman[0],pacman[1]=user.move(direction, pacman[0],pacman[1])
        if req=='down':
            if (user.canMove(math.ceil(pacman[0] + .25), pacman[1]) and pacman[1]%1.0 ==0):
                direction='down'
            pacman[0],pacman[1]=user.move(direction, pacman[0],pacman[1])

        if gameBoard[int(pacman[0])][int(pacman[1])] == 1:
            coinCount += 10
            print("The current coins:", coinCount)
            gameBoard[int(pacman[0])][int(pacman[1])] = 2
            sound_delay = 40
            if coinCount%sound_delay==10:
                eating_Sound= mixer.Sound('pacman_chomp.wav')
                eating_Sound.set_volume(0.2)
                eating_Sound.play()
        if gameBoard[int(pacman[0])][int(pacman[1])] == 4:
            coinCount+= 200
            print("The current coins:", coinCount)
            gameBoard[int(pacman[0])][int(pacman[1])] = 2
            fruit_Sound = mixer.Sound('pacman_eatfruit.wav')
            fruit_Sound.set_volume(0.2)
            fruit_Sound.play()
        if gameBoard[int(pacman[0])][int(pacman[1])] == 3:
            user.died_wait()
        time.sleep(0.03)
        user = PacMan(direction, gameBoard, square, screen, pacman,coinCount,length,width)
if __name__ == '__main__':
    main()
