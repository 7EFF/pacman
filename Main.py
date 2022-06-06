import pickle
import pygame
import sys

pygame.init()
from pygame import mixer
from pygame.locals import *

pygame.font.init()
pygame.mixer.init()
from ghosts_class import *
import time
import socket
import select


class PacMan:
    def __init__(self, my_socket, direction, gameBoard, square, screen, pacman, coinCount, length, width, pacspeed,
                 eatGhosts, mouthChange,wager,balance):
        self.my_socket = my_socket
        self.direction = direction
        self.gameBoard = gameBoard
        self.square = square
        self.screen = screen
        self.pacman = pacman
        self.coinCount = coinCount
        self.length = length
        self.width = width
        self.g_pos = []
        self.pacspeed = pacspeed
        self.ghosts = []
        self.eatGhosts = eatGhosts
        self.mouthChange = mouthChange
        self.ghostLeave = 0
        self.sentData = False
        self.RecievedData = False
        self.wager=wager
        self.balance=balance
        self.Queue_Again=False

    ###########################SET & GET###########################

    #def setAsDefault(self):


    def set_My_socket(self,my_socket):
        self.my_socket=my_socket

    def setMouthChange(self, mouthChange):
        self.mouthChange = mouthChange

    def setDirection(self, direction):
        self.direction = direction

    def setPacMan(self, pacman):
        self.pacman = pacman

    def setCoinCount(self, coinCount):
        self.coinCount = coinCount

    def setEatGhosts(self, eatGhost):
        self.eatGhosts = eatGhost

    ###########################SET & GET###########################

    ###########################SERVER###########################

    ###########################SERVER###########################

    ###########################MOVEMENT###########################

    def canMove(self, row, col):
        if self.gameBoard[int(row)][int(col)] != 0:
            if self.gameBoard[int(row)][int(col)] != 4:
                return True
        return False

    def move(self, direction, row, col):
        if direction == 'up':
            if self.canMove(math.floor(row - self.pacspeed), col) and col % 1.0 == 0:
                row -= self.pacspeed
                self.setMouthChange(self.mouthChange + 1)
        elif direction == 'right':
            if self.canMove(row, math.ceil(col + self.pacspeed)) and row % 1.0 == 0:
                col += self.pacspeed
                self.setMouthChange(self.mouthChange + 1)
        elif direction == 'left':
            if self.canMove(row, math.floor(col - self.pacspeed)) and row % 1.0 == 0:
                col -= self.pacspeed
                self.setMouthChange(self.mouthChange + 1)
        else:
            if self.canMove(math.ceil(row + self.pacspeed), col) and col % 1.0 == 0:
                row += self.pacspeed
                self.setMouthChange(self.mouthChange + 1)
        return row, col

    ###########################MOVEMENT###########################

    ###########################GHOSTS###########################

    def stopGrouping(self):
        ghostsArray = []
        for gh in self.ghosts:
            ghostsArray.append(gh)
        i = 0
        while i < 4:
            i = i + 1
            R_diff = ghostsArray[0].getRow() - ghostsArray[1].getRow()
            C_diff = ghostsArray[0].getCol() - ghostsArray[1].getCol()
            if abs(R_diff) < 0.5 or abs(C_diff) < 0.5:
                if ghostsArray[0].getBehavior() != 'Random' and ghostsArray[0].getBehavior() != 'Leave':
                    ghostsArray[0].setBehavior('Random')

    def bigCoinEaten(self):
        for gh in self.ghosts:
            gh.drawGhost()
            gh.bigCoinEaten()

    def move_Ghosts(self):
        for gh in self.ghosts:
            gh.movementBehaves()
            gh.drawGhost()

    def make_Ghosts(self):
        self.ghosts = [Ghost(self, 13, 14, 'yellow', self.pacman[0], self.pacman[1]),
                       Ghost(self, 14, 13, 'pink', self.pacman[0], self.pacman[1]),
                       Ghost(self, 14, 14, 'cyan', self.pacman[0], self.pacman[1]),
                       Ghost(self, 13, 13, 'red', self.pacman[0], self.pacman[1])]
        for gh in self.ghosts:
            gh.drawGhost()

    ###########################GHOSTS###########################

    ###########################DRAWING###########################

    def pacAnimation(self):
        Directory = "PacPics\pacman_"
        if 50 <= self.mouthChange % 100 < 100:
            Directory = Directory + "big_"
        else:
            Directory = Directory + "small_"
        if self.direction == 'left':
            Directory = Directory + "left.png"
        elif self.direction == 'right':
            Directory = Directory + "right.png"
        elif self.direction == 'up':
            Directory = Directory + "up.png"
        elif self.direction == 'down':
            Directory = Directory + "down.png"
        pac_Pic = pygame.image.load(Directory).convert()
        pac_Pic = pygame.transform.scale(pac_Pic, (int(self.square * 1.3), int(self.square * 1.3)))
        self.screen.blit(pac_Pic, (
        math.floor(self.pacman[1] * self.square), math.floor(self.pacman[0] * self.square), self.square, self.square))

    def Board(self, background, BigCoinChange, Time_Counter):
        self.screen.fill((0, 0, 0))
        coinsCount = 0
        self.screen.blit(background, (0, 0))
        for i in range(len(self.gameBoard[0])):
            for j in range(len(self.gameBoard[1])):
                if self.gameBoard[i][j] == 1:
                    pygame.draw.circle(self.screen, [248, 152, 128],
                                       (j * self.square + self.square / 2, i * self.square + self.square / 2),
                                       self.square / 5)
                    coinsCount += 1
                elif self.gameBoard[i][j] == 2:
                    pygame.draw.circle(self.screen, [0, 0, 0],
                                       (j * self.square + self.square / 2, i * self.square + self.square / 2),
                                       self.square / 3)
                elif self.gameBoard[i][j] == 3 and BigCoinChange < 50:
                    pygame.draw.circle(self.screen, [248, 152, 128],
                                       (j * self.square + self.square / 2, i * self.square + self.square / 2),
                                       self.square / 2)
                else:
                    self.g_pos.append([i, j])
        if self.mouthChange == 100:
            self.setMouthChange(0)
        self.pacAnimation()
        Font = pygame.font.SysFont('bn elements', math.floor(self.square / 1.5))
        text = Font.render('COINS: {}'.format(self.coinCount), True, (255, 255, 0))
        textRect = text.get_rect()
        textRect.center = (2 * self.square, 17.5 * self.square)
        self.screen.blit(text, textRect)
        self.move_Ghosts()
        self.stopGrouping()
        pygame.display.flip()
        if coinsCount == 0:
            self.winning(Time_Counter)

    def Intro_Render(self):
        while 1:
            self.screen.fill((0, 0, 0))
            player = pygame.image.load("intro_pic.png")
            player = pygame.transform.scale(player, (self.width, self.length))
            self.screen.blit(player, (0, 0))
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_SPACE:
                        intro_sound = mixer.Sound('Sounds\pacman_beginning.wav')
                        intro_sound.set_volume(0.2)
                        intro_sound.play()
                        for i in range(len(self.gameBoard[0])):
                            for j in range(len(self.gameBoard[1])):
                                pygame.draw.rect(self.screen, [0, 0, 0],
                                                 (j * self.square, i * self.square, self.square, self.square))
                                pygame.draw.rect(self.screen, [0, 0, 77], (
                                j * self.square, i * self.square, int(self.square / 1.5), int(self.square / 1.5)))
                            time.sleep(4 / len(self.gameBoard[0]))
                            if i == len(self.gameBoard[0]):
                                break
                            pygame.display.update()
                        return
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    ###########################DRAWING###########################

    ###########################END_OF_GAME###########################

    def died_wait(self, Time_Counter):
        death_Sound = mixer.Sound('Sounds\pacman_death.wav')
        death_Sound.set_volume(0.2)
        death_Sound.play()
        msg=""
        printed_Money=False
        self.RecievedData = False
        while 1:
            rlist, slist, xlist = select.select([self.my_socket], [], [], 0.1)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.my_socket.close()
                        pygame.quit()
                        sys.exit()
                    if event.key == K_q and msg == "You have lost":
                        self.my_socket.send("Queue Again".encode())
                        self.my_socket.close()
                        self.Queue_Again=True
                        return
                    if event.key == K_s and msg == "You have lost":
                        self.my_socket.send("Spectate".encode())
                if event.type == QUIT:
                    self.my_socket.close()
                    pygame.quit()
                    sys.exit()
            self.screen.fill((0, 0, 0))
            Font = pygame.font.SysFont('arial black', self.square)
            for s in rlist:
                msg = s.recv(1024).decode()
                print(msg)
                self.RecievedData = True
            if self.RecievedData == False:
                msg = 'YOU DIED, WAITING FOR OPPONENT'
            text = Font.render(msg, True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2, self.width / 2)
            self.screen.blit(text, textRect)
            pygame.display.update()
            if self.sentData == False:
                data_to_send = (self.coinCount,Time_Counter)
                self.my_socket.send(pickle.dumps(data_to_send))
                '''self.my_socket.send(str(self.coinCount).encode())
                time.sleep(0.05)
                self.my_socket.send(str(Time_Counter).encode())'''
                self.sentData = True
            if msg == "You have lost":
                if printed_Money==False:
                    self.balance = self.balance - self.wager
                    reward = math.floor(0.5 * self.wager)
                    self.balance = self.balance + reward
                    print("Your balance is now:", self.balance)
                    printed_Money = True
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            self.my_socket.send(str(0).encode())
                            time.sleep(0.05)
                            self.my_socket.send(str(Time_Counter).encode())
                            self.my_socket.close()
                    if event.type == QUIT:
                        self.my_socket.send(str(0).encode())
                        time.sleep(0.5)
                        self.my_socket.send(str(Time_Counter).encode())
                        self.my_socket.close()
                        pygame.quit()
                        sys.exit()
                Font = pygame.font.SysFont('arial black', int(1.5*self.square))
                text = Font.render('PRESS Q TO QUEUE AGAIN', True, (255, 255, 0))
                textRect = text.get_rect()
                textRect.center = (self.length / 2, self.width / 1.5)
                self.screen.blit(text, textRect)
                text = Font.render('PRESS S TO SPECTATE', True, (255, 255, 0))
                textRect = text.get_rect()
                textRect.center = (self.length / 2, self.width / 2.5)
                self.screen.blit(text, textRect)
                pygame.display.update()
            if msg == "You have won !":
                if printed_Money==False:
                    self.balance = self.balance - self.wager
                    reward = math.floor(1.5 * self.wager)
                    self.balance = self.balance + reward
                    print("Your balance is now:", self.balance)
                    printed_Money = True


    def winning(self, Time_Counter):
        msg = ""
        printed_Money=False
        while 1:
            rlist, slist, xlist = select.select([self.my_socket], [], [], 0.1)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_q and msg == "You have lost":
                        print("bulbul")
                        self.my_socket.send("Queue Again".encode())
                        self.my_socket.close()
                        self.Queue_Again=True
                        return
                    if event.key == K_s and msg == "You have lost":
                        self.my_socket.send("Spectate".encode())
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            self.screen.fill((0, 0, 0))
            Font = pygame.font.SysFont('arial black', int(1.5*self.square))
            for s in rlist:
                msg = s.recv(1024).decode()
                print(msg)
                self.RecievedData = True
            if self.RecievedData == False:
                msg = 'YOU HAVE EATEN EVERY COIN, WAITING FOR RESULT'
            text = Font.render(msg, True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2, self.width / 2)
            self.screen.blit(text, textRect)
            pygame.display.update()
            if self.sentData == False:
                data_to_send = (self.coinCount, Time_Counter)
                self.my_socket.send(pickle.dumps(data_to_send))
                '''self.my_socket.send(str(self.coinCount).encode())
                time.sleep(0.05)
                self.my_socket.send(str(Time_Counter).encode())'''
                self.sentData = True
            if msg == "You have lost":
                if printed_Money==False:
                    self.balance = self.balance - self.wager
                    reward = math.floor(0.75 * self.wager)
                    self.balance = self.balance + reward
                    print("Your balance is now:", self.balance)
                    printed_Money = True
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            self.my_socket.send(str(0).encode())
                            time.sleep(0.05)
                            self.my_socket.send(str(Time_Counter).encode())
                            self.my_socket.close()
                    if event.type == QUIT:
                        self.my_socket.send(str(0).encode())
                        time.sleep(0.5)
                        self.my_socket.send(str(Time_Counter).encode())
                        self.my_socket.close()
                        pygame.quit()
                        sys.exit()
                Font = pygame.font.SysFont('arial black', int(1.5 * self.square))
                text = Font.render('PRESS Q TO QUEUE AGAIN', True, (255, 255, 0))
                textRect = text.get_rect()
                textRect.center = (self.length / 2, self.width / 1.5)
                self.screen.blit(text, textRect)
                text = Font.render('PRESS S TO SPECTATE', True, (255, 255, 0))
                textRect = text.get_rect()
                textRect.center = (self.length / 2, self.width / 2.5)
                self.screen.blit(text, textRect)
                pygame.display.update()
            if msg == "You have won !":
                if printed_Money==False:
                    self.balance = self.balance - self.wager
                    reward = math.floor(2*self.wager)
                    self.balance = self.balance+reward
                    print("Your balance is now:",self.balance)
                    printed_Money = True

###########################END_OF_GAME###########################


def main():
    balance=1000
    wager = int(input("Your balance is 1000$, how much would you like to bet?"))
    print("Your balance is now", balance-wager)
    square = 20
    pacspeed = 1 / 64
    clock = pygame.time.Clock()
    clock.tick(30)
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
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
        [0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 5, 5, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 4, 4, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
        [0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 3, 0, 0, 0, 0, ],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
        [0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]
        # 0=קיר שאי אפשר לעבור
        # 1=מטבע
        # 2=מקום שאפשר ללכת בוא אבל בלי מטבעות
        # 3=מטסעות גדולים
        # 4=מקום שרק רוחות עוברות בו
    ]
    [length, width] = [31 * square, 28 * square]
    screen = pygame.display.set_mode((width, length))
    pacman = [23, 13.5]
    pygame.display.set_caption("PacMan-Final Project")
    direction = 'up'
    coinCount = 0
    req = 'up'
    blueCounter = 0
    eatGhosts = False
    background = pygame.image.load('backGround.png').convert()
    background = pygame.transform.scale(background, (width, length))
    mouthChange = 0
    my_socket = socket.socket()
    user = PacMan(my_socket, direction, gameBoard, square, screen, pacman, coinCount, length, width, pacspeed,eatGhosts, mouthChange,wager,balance)
    user.Intro_Render()
    my_socket.connect(('127.0.0.1', 5555))
    my_socket.send("go".encode())
    Time_Counter = 1
    BigCoinChange = 0
    while 1:
        if user.RecievedData == False:
            Font = pygame.font.SysFont('arial black', int(square))
            text = Font.render('WAITING FOR ANOTHER PERSON', True, (255, 255, 0))
            textRect = text.get_rect()
            textRect.center = (length / 2, width / 2)
            screen.blit(text, textRect)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        my_socket.send(str(0).encode())
                        time.sleep(0.05)
                        my_socket.send(str(Time_Counter).encode())
                        my_socket.close()
                        running = False
                if event.type == QUIT:
                    my_socket.send(str(0).encode())
                    time.sleep(0.05)
                    my_socket.send(str(Time_Counter).encode())
                    my_socket.close()
                    pygame.quit()
                    sys.exit()

            rlist, slist, xlist = select.select([user.my_socket], [], [], 0.1)
            for s in rlist:
                msg = s.recv(1024).decode()
                print(msg)
                user.RecievedData = True
                user.make_Ghosts()
        else:
            Time_Counter += 1
            BigCoinChange += 1
            user.Board(background, BigCoinChange, Time_Counter)
            if BigCoinChange == 100:
                BigCoinChange = 0
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        my_socket.send(str(0).encode())
                        time.sleep(0.05)
                        my_socket.send(str(Time_Counter).encode())
                        my_socket.close()
                        running = False
                    elif event.key == K_UP:
                        req = 'up'
                    elif event.key == K_RIGHT:
                        req = 'right'
                    elif event.key == K_LEFT:
                        req = 'left'
                    elif event.key == K_DOWN:
                        req = 'down'
                if event.type == QUIT:
                    my_socket.send(str(0).encode())
                    time.sleep(0.05)
                    my_socket.send(str(Time_Counter).encode())
                    my_socket.close()
                    pygame.quit()
                    sys.exit()

            if req == 'up':
                if (user.canMove(math.floor(pacman[0] - pacspeed), pacman[1]) and pacman[1] % 1.0 == 0):
                    direction = 'up'
            if req == 'right':
                if (user.canMove(pacman[0], math.ceil(pacman[1] + pacspeed)) and pacman[0] % 1.0 == 0):
                    direction = 'right'
            if req == 'left':
                if (user.canMove(pacman[0], math.floor(pacman[1] - pacspeed)) and pacman[0] % 1.0 == 0):
                    direction = 'left'
            if req == 'down':
                if (user.canMove(math.ceil(pacman[0] + pacspeed), pacman[1]) and pacman[1] % 1.0 == 0):
                    direction = 'down'
            pacman[0], pacman[1] = user.move(direction, pacman[0], pacman[1])
            if pacman[1] < 0.015625 and direction == 'left':
                pacman[0], pacman[1] = user.move(direction, pacman[0], 27.484375)
            if pacman[1] > 26.984375 and direction == 'right':
                pacman[0], pacman[1] = user.move(direction, pacman[0], 0.015625)
                gameBoard[int(pacman[0])][27] = 2
            if gameBoard[int(pacman[0])][int(pacman[1])] == 1:
                coinCount += 10
                gameBoard[int(pacman[0])][int(pacman[1])] = 2
                if pygame.mixer.get_busy() == False:
                    eating_Sound = mixer.Sound('Sounds\pacman_chomp.wav')
                    eating_Sound.set_volume(0.5)
                    eating_Sound.play()
            if gameBoard[int(pacman[0])][int(pacman[1])] == 3:
                coinCount += 200
                gameBoard[int(pacman[0])][int(pacman[1])] = 2
                fruit_Sound = mixer.Sound('Sounds\pacman_eatfruit.wav')
                fruit_Sound.set_volume(0.6)
                fruit_Sound.play()
                user.bigCoinEaten()
                eatGhosts = True
                blueCounter = 0
            for gh in user.ghosts:
                died = gh.ifTouched()
                if died == 'died':
                    user.died_wait(Time_Counter)
                    if user.Queue_Again==True:
                        user.Intro_Render()
                        my_socket = socket.socket()
                        my_socket.connect(('127.0.0.1', 5555))
                        my_socket.send("go".encode())
                        user.set_My_socket(my_socket)
                        pacman = [23, 13.5]
                        direction = 'up'
                        coinCount = 0
                        req = 'up'
                        blueCounter = 0
                        eatGhosts = False
                        mouthChange = 0
                        Time_Counter = 1
                        BigCoinChange = 0
                        gameBoard = [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
                            [0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
                            [0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 5, 5, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 4, 4, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
                            [0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 3, 0, 0, 0, 0, ],
                            [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
                            [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
                            [0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
                            [0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, ],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, ],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]
                        ]
                        print(user.balance)
                        user = PacMan(my_socket, direction, gameBoard, square, screen, pacman, coinCount, length, width,pacspeed, eatGhosts, mouthChange,user.wager,user.balance)
                if died == 'eaten':
                    gh.eatenBlue()
                    coinCount += 400
                    eat_ghost = mixer.Sound('Sounds\pacman_eatghost.wav')
                    eat_ghost.set_volume(0.6)
                    eat_ghost.play()
            if eatGhosts:
                if blueCounter == 3000:
                    for gh in user.ghosts:
                        gh.blueOver()
                    blueCounter = 0
                    eatGhosts = False
                if blueCounter >= 2200 and blueCounter % 160 == 0:
                    for gh in user.ghosts:
                        if gh.getDied() == False:
                            gh.flickerToBLUE()
                if blueCounter >= 2200 and blueCounter % 160 == 80:
                    for gh in user.ghosts:
                        gh.flickerToOG()
                blueCounter += 1
            user.setPacMan(pacman)
            user.setCoinCount(coinCount)
            user.setDirection(direction)
            user.setEatGhosts(eatGhosts)


if __name__ == '__main__':
    main()
