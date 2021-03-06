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

start_time = 0


class PacMan:
    def __init__(self, my_socket, direction, gameBoard, square, screen, pacman, coinCount, length, width, pacspeed,
                 eatGhosts, mouthChange, wager, balance, has_died, all_eaten, username, password):
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
        self.wager = wager
        self.balance = balance
        self.Queue_Again = False
        self.nextGame = False
        self.has_died = has_died
        self.all_eaten = all_eaten
        self.username = username
        self.password = password
        self.msg = ""
        self.win = False
        self.Request = ""
        self.nowSpectator=False

    ###########################SET & GET###########################

    def getMsg(self):
        return self.msg

    def set_My_socket(self, my_socket):
        self.my_socket = my_socket

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

    def getWager(self):
        return self.wager

    ###########################SET & GET###########################

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
            math.floor(self.pacman[1] * self.square), math.floor(self.pacman[0] * self.square), self.square,
            self.square))

    def Board(self, background, BigCoinChange):
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
            self.winning()
            self.died_wait()  # ???? ?????? ???? ??????
            self.screen.fill((0, 0, 0))  # ?????????? ???????? ?????????? ???????? ??winning
            back_img = pygame.image.load("end_background.jpg")
            back_img = pygame.transform.scale(back_img, (self.width, self.length))
            self.screen.blit(back_img, (0, 0))
            pygame.display.update()
            if self.nextGame == True:  # ???? ????????
                rlist, slist, xlist = select.select([self.my_socket], [], [], 0.1)
                for s in rlist:
                    msg = s.recv(1024).decode()
                    print(msg)
                    self.nextGame = False
            if self.Queue_Again == True:  # ???? ?????????? ?????????? ???????? ?????????? ??????
                self.wager_screen()
                my_socket = socket.socket()
                my_socket.connect(('127.0.0.1', 5555))
                self.set_My_socket(my_socket)
                self.Queue_Again = False
            self.Intro_Render()
            self.my_socket.send("go".encode())
            print("sent message")
            pacman = [23, 13.5]
            direction = 'up'
            coinCount = 0
            req = 'up'
            blueCounter = 0
            eatGhosts = False
            mouthChange = 0
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
            player = PacMan(self.my_socket, direction, gameBoard, self.square, self.screen, pacman, coinCount,
                            self.length, self.width, self.pacspeed, eatGhosts, mouthChange, self.wager, self.balance,
                            False, True, self.username, self.password)
            player.RecievedData = False

    def Intro_Render(self):
        while 1:
            self.screen.fill((0, 0, 0))
            intro_img = pygame.image.load("intro_pic.png")
            intro_img = pygame.transform.scale(intro_img, (self.width, self.length))
            self.screen.blit(intro_img, (0, 0))
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

    def button(self, screen, position, text):
        font = pygame.font.SysFont("Arial", 50)
        text_render = font.render(text, True, (255, 0, 0))
        x, y, w, h = text_render.get_rect()
        x, y = position
        pygame.draw.line(screen, (150, 150, 150), (x, y), (x + w, y), 5)
        pygame.draw.line(screen, (150, 150, 150), (x, y - 2), (x, y + h), 5)
        pygame.draw.line(screen, (50, 50, 50), (x, y + h), (x + w, y + h), 5)
        pygame.draw.line(screen, (50, 50, 50), (x + w, y + h), [x + w, y], 5)
        pygame.draw.rect(screen, (100, 100, 100), (x, y, w, h))
        return screen.blit(text_render, (x, y))

    def wager_screen(self):
        string = ""
        isStupid = False
        running = True
        while 1:
            self.screen.fill((0, 0, 30))
            back_img = pygame.image.load("end_background.jpg")
            back_img = pygame.transform.scale(back_img, (self.width, self.length))
            self.screen.blit(back_img, (0, 0))
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_BACKSPACE:
                        string = string[:-1]
                    elif event.key == pygame.K_RETURN and string != "":
                        running = True
                        self.wager = int(string)
                        if int(self.wager) <= self.balance:
                            self.screen.fill((0, 0, 30))
                            b1 = self.button(self.screen, (400, 400), "Change")
                            b2 = self.button(self.screen, (100, 400), "Continue")
                            while running:
                                for event in pygame.event.get():
                                    if event.type == KEYDOWN:
                                        if event.key == K_ESCAPE:
                                            pygame.quit()
                                            sys.exit()
                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        if b1.collidepoint(pygame.mouse.get_pos()):
                                            string = ""
                                            running = False
                                            break
                                        elif b2.collidepoint(pygame.mouse.get_pos()):
                                            intro_sound = mixer.Sound('Sounds\pacman_beginning.wav')
                                            intro_sound.set_volume(0.2)
                                            intro_sound.play()
                                            for i in range(len(self.gameBoard[0])):
                                                for j in range(len(self.gameBoard[1])):
                                                    pygame.draw.rect(self.screen, [0, 0, 0],
                                                                     (j * self.square, i * self.square, self.square,
                                                                      self.square))
                                                    pygame.draw.rect(self.screen, [0, 0, 77], (
                                                        j * self.square, i * self.square, int(self.square / 1.5),
                                                        int(self.square / 1.5)))
                                                time.sleep(4 / len(self.gameBoard[0]))
                                                if i == len(self.gameBoard[0]):
                                                    break
                                                pygame.display.update()
                                            return
                                    if event.type == QUIT:
                                        pygame.quit()
                                        sys.exit()
                                Font = pygame.font.SysFont('arial black', int(self.square * 1.5))
                                msg = "Your wager is: "
                                msg += string
                                text = Font.render(msg, True, (255, 0, 0))
                                textRect = text.get_rect()
                                textRect.center = (self.length / 2, self.width / 5)
                                self.screen.blit(text, textRect)
                                msg = "Your Balance is now: "
                                msg += str(self.balance - self.wager)
                                text = Font.render(msg, True, (255, 0, 0))
                                textRect = text.get_rect()
                                textRect.center = (self.length / 2, self.width / 2.5)
                                self.screen.blit(text, textRect)
                                text = Font.render("Want to continue?", True, (255, 0, 0))
                                textRect = text.get_rect()
                                textRect.center = (self.length / 2, self.width / 1.5)
                                self.screen.blit(text, textRect)
                                pygame.display.update()
                        else:
                            isStupid = True
                    if event.key == K_1 or event.key == K_2 or event.key == K_3 or event.key == K_4 or event.key == K_5 or event.key == K_6 or event.key == K_7 or event.key == K_8 or event.key == K_9 or event.key == K_0:
                        string += event.unicode
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            Font = pygame.font.SysFont('arial black', int(self.square * 1.5))
            text = Font.render(string, True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2 + 10, self.width / 2)
            self.screen.blit(text, textRect)
            text = Font.render("Wager:", True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (60, self.width / 2)
            self.screen.blit(text, textRect)
            prt = "Balance: "
            prt += str(self.balance)
            text = Font.render(prt, True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (150, 50)
            self.screen.blit(text, textRect)
            if isStupid == True:
                text = Font.render("Your wager was higher", True, (255, 0, 0))
                textRect = text.get_rect()
                textRect.center = (200, 400)
                self.screen.blit(text, textRect)
                text = Font.render("than Your balance", True, (255, 0, 0))
                textRect = text.get_rect()
                textRect.center = (200, 450)
                self.screen.blit(text, textRect)
            pygame.display.update()

    def spectate(self):
        msg=""
        while 1:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_y:
                        data_to_send = ("yes", self.wager)
                        self.my_socket.send(pickle.dumps(data_to_send))
                        print("betted on", username)
                        msg = "Waiting for results"
                    if event.key == K_n:
                        data_to_send = ("no", self.wager)
                        self.my_socket.send(pickle.dumps(data_to_send))
                if event.type == QUIT:
                    self.my_socket.close()
                    pygame.quit()
                    sys.exit()
            if msg == "Waiting for results":
                self.screen.fill((0, 0, 0))
                back_img = pygame.image.load("end_background.jpg")
                back_img = pygame.transform.scale(back_img, (self.width, self.length))
                self.screen.blit(back_img, (0, 0))
                Font = pygame.font.SysFont('arial black', self.square)
                text = Font.render(msg, True, (255, 0, 0))
                textRect = text.get_rect()
                textRect.center = (self.length / 2, self.width / 4)
                self.screen.blit(text, textRect)
                pygame.display.update()
            rlist, slist, xlist = select.select([self.my_socket], [], [], 0.1)
            for s in rlist:
                data_from_client = pickle.loads(s.recv(1024))  # ???????? ???? ?????????????? ?????? ???????? ???? ??????????
                username, games_played, games_won = data_from_client
                if username != self.username:
                    print(username, games_played, games_won)
                    self.screen.fill((0, 0, 0))
                    back_img = pygame.image.load("end_background.jpg")
                    back_img = pygame.transform.scale(back_img, (self.width, self.length))
                    self.screen.blit(back_img, (0, 0))
                    Font = pygame.font.SysFont('arial black', self.square)
                    msg = "username, games played, games won"
                    text = Font.render(msg, True, (255, 0, 0))
                    textRect = text.get_rect()
                    textRect.center = (self.length / 2, self.width / 4)
                    self.screen.blit(text, textRect)
                    Font = pygame.font.SysFont('arial black', math.floor(self.square * 1.5))
                    msg = username + " " + str(games_played) + " " + str(games_won)
                    text = Font.render(msg, True, (255, 0, 0))
                    textRect = text.get_rect()
                    textRect.center = (self.length / 2, self.width / 2)
                    self.screen.blit(text, textRect)
                    Font = pygame.font.SysFont('arial black', self.square)
                    msg = "Press Y for bet, press N to continue"
                    text = Font.render(msg, True, (255, 0, 0))
                    textRect = text.get_rect()
                    textRect.center = (self.length / 2, math.floor(self.width / 1.3))
                    self.screen.blit(text, textRect)
                    pygame.display.update()
                if username=="Your bet has lost" or username=="Your bet has won":
                    self.screen.fill((0, 0, 0))
                    back_img = pygame.image.load("end_background.jpg")
                    back_img = pygame.transform.scale(back_img, (self.width, self.length))
                    self.screen.blit(back_img, (0, 0))
                    Font = pygame.font.SysFont('arial black', math.floor(self.square*1.5))
                    msg = username
                    text = Font.render(msg, True, (255, 0, 0))
                    textRect = text.get_rect()
                    textRect.center = (self.length / 2, self.width / 2)
                    self.screen.blit(text, textRect)
                    pygame.display.update()

    ###########################DRAWING###########################

    ###########################END_OF_GAME###########################

    def died_wait(self):
        death_Sound = mixer.Sound('Sounds\pacman_death.wav')
        death_Sound.set_volume(0.2)
        death_Sound.play()
        msg = ""
        printed_Money = False
        self.RecievedData = False
        while 1:
            rlist, slist, xlist = select.select([self.my_socket], [], [], 0.1)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        end_time = time.time()
                        Time_Counter = int(end_time - start_time)
                        data_to_send = (0, Time_Counter, self.wager, self.username, False)
                        self.my_socket.send(pickle.dumps(data_to_send))
                        self.my_socket.close()
                        pygame.quit()
                        sys.exit()
                    if event.key == K_q and msg == "You have lost":
                        self.my_socket.close()
                        self.Queue_Again = True
                        return
                    if event.key == K_s and msg == "You have lost":
                        self.my_socket.close()
                        self.nowSpectator=True
                        return
                if event.type == QUIT:
                    end_time = time.time()
                    Time_Counter = int(end_time - start_time)
                    data_to_send = (0, Time_Counter, self.wager, self.username, False)
                    self.my_socket.send(pickle.dumps(data_to_send))
                    self.my_socket.close()
                    pygame.quit()
                    sys.exit()
            self.screen.fill((0, 0, 0))
            back_img = pygame.image.load("end_background.jpg")
            back_img = pygame.transform.scale(back_img, (self.width, self.length))
            self.screen.blit(back_img, (0, 0))
            Font = pygame.font.SysFont('arial black', self.square)
            for s in rlist:
                msg = s.recv(1024).decode()
                print(msg)
                self.RecievedData = True
            if not self.RecievedData:
                msg = 'YOU DIED, WAITING FOR OPPONENT'
            text = Font.render(msg, True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2, self.width / 2)
            self.screen.blit(text, textRect)
            pygame.display.update()
            if not self.sentData:
                end_time = time.time()
                Time_Counter = int(end_time - start_time)
                print(Time_Counter, "sending time")
                data_to_send = (self.coinCount, Time_Counter, self.wager, self.username, False)
                self.my_socket.send(pickle.dumps(data_to_send))
                self.sentData = True
            if msg == "You have lost":
                if printed_Money == False:
                    self.balance = self.balance - self.wager
                    print("Your balance is now:", self.balance)
                    printed_Money = True
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
            if msg == "You have won this duel!":
                self.win = True
                self.Queue_Again = False
                return

    def winning(self):
        death_Sound = mixer.Sound('Sounds\pacman_death.wav')
        death_Sound.set_volume(0.2)
        death_Sound.play()
        msg = ""
        printed_Money = False
        self.RecievedData = False
        while 1:
            rlist, slist, xlist = select.select([self.my_socket], [], [], 0.1)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        end_time = time.time()
                        Time_Counter = int(end_time - start_time)
                        data_to_send = (0, Time_Counter, self.wager, self.username, False)
                        self.my_socket.send(pickle.dumps(data_to_send))
                        self.my_socket.close()
                        pygame.quit()
                        sys.exit()
                    if event.key == K_q and msg == "You have lost":
                        self.my_socket.close()
                        self.Queue_Again = True
                        return
                    if event.key == K_s and msg == "You have lost":
                        self.my_socket.close()
                        self.nowSpectator = True
                        return
                if event.type == QUIT:
                    end_time = time.time()
                    Time_Counter = int(end_time - start_time)
                    data_to_send = (0, Time_Counter, self.wager, self.username, False)
                    self.my_socket.send(pickle.dumps(data_to_send))
                    self.my_socket.close()
                    pygame.quit()
                    sys.exit()
            self.screen.fill((0, 0, 0))
            back_img = pygame.image.load("end_background.jpg")
            back_img = pygame.transform.scale(back_img, (self.width, self.length))
            self.screen.blit(back_img, (0, 0))
            Font = pygame.font.SysFont('arial black', self.square)
            for s in rlist:
                msg = s.recv(1024).decode()
                print(msg)
                self.RecievedData = True
            if not self.RecievedData:
                msg = 'YOU HAVE EATEN EVERY COIN, WAITING FOR RESULT'
            text = Font.render(msg, True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2, self.width / 2)
            self.screen.blit(text, textRect)
            pygame.display.update()
            if not self.sentData:
                end_time = time.time()
                Time_Counter = int(end_time - start_time)
                data_to_send = (self.coinCount, Time_Counter, self.wager, self.username, False)
                self.my_socket.send(pickle.dumps(data_to_send))
                self.sentData = True
            if msg == "You have lost":
                if printed_Money == False:
                    self.balance = self.balance - self.wager
                    print("Your balance is now:", self.balance)
                    printed_Money = True
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
            if msg == "You have won this duel!":
                self.win = True
                self.Queue_Again = False
                return

    ###########################END_OF_GAME###########################

    ###########################SQL###########################

    def verify(self):
        inputCount = 0
        signing = ""
        username = ""
        password = ""
        string = ""
        msg = "Play or spectate?"
        while 1:
            self.screen.fill((0, 0, 30))
            back_img = pygame.image.load("end_background.jpg")
            back_img = pygame.transform.scale(back_img, (self.width, self.length))
            self.screen.blit(back_img, (0, 0))
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_BACKSPACE:
                        string = string[:-1]
                    elif event.key == pygame.K_RETURN and string != "":
                        if inputCount == 0:
                            if string == "play" or string == "spectate":
                                self.Request = string
                                Request = string
                                inputCount = 1
                                msg = "Log in or Sign up?"
                                string = ""
                                break
                        if inputCount == 1:
                            if string == "sign up" or string == "log in":
                                signing = string
                                inputCount = 2
                                msg = "Enter username"
                                string = ""
                                break
                            else:
                                inputCount = 1
                                string = ""
                                break
                        if inputCount == 2:
                            username = string
                            inputCount = 3
                            msg = "Enter password"
                            string = ""
                            break
                        if inputCount == 3:
                            password = string
                            running = True
                            data_to_send = (signing, username, password)
                            self.my_socket.send(pickle.dumps(data_to_send))
                            msg = "Waiting for verifacation"
                            while running == True:
                                self.screen.fill((0, 0, 30))
                                back_img = pygame.image.load("end_background.jpg")
                                back_img = pygame.transform.scale(back_img, (self.width, self.length))
                                self.screen.blit(back_img, (0, 0))
                                Font = pygame.font.SysFont('arial black', self.square)
                                text = Font.render(msg, True, (255, 0, 0))
                                textRect = text.get_rect()
                                textRect.center = (self.length / 2, self.width / 2)
                                self.screen.blit(text, textRect)
                                pygame.display.update()
                                rlist, slist, xlist = select.select([self.my_socket], [], [], 0.1)
                                for s in rlist:
                                    data_from_client = pickle.loads(s.recv(1024))  # ???????? ???? ?????????????? ?????? ???????? ???? ??????????
                                    msg, self.balance = data_from_client
                                    print(msg)
                                    if msg == "Incorrect password or name" or msg == "Name already exists":
                                        msg = "Enter username"
                                        running = False
                                    else:
                                        self.my_socket.send(Request.encode())
                                        self.username = username
                                        self.password = password
                                        return
                            inputCount = 2
                            string = ""
                    else:
                        string += event.unicode
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            Font = pygame.font.SysFont('arial black', int(self.square * 1.5))
            text = Font.render(string, True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2, self.width / 2)
            self.screen.blit(text, textRect)
            Font = pygame.font.SysFont('arial black', self.square)
            text = Font.render(msg, True, (255, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.length / 2, 60)
            self.screen.blit(text, textRect)
            pygame.display.update()


###########################SQL###########################


def main():
    global start_time
    username = ""
    balance = 1000
    correctPassword = False
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
        # 0=?????? ?????? ???????? ??????????
        # 1=????????
        # 2=???????? ?????????? ???????? ?????? ?????? ?????? ????????????
        # 3=???????????? ????????????
        # 4=???????? ?????? ?????????? ???????????? ????
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
    wager = 0
    player = PacMan(my_socket, direction, gameBoard, square, screen, pacman, coinCount, length, width, pacspeed,
                    eatGhosts, mouthChange, wager, balance, False, False, username, "")
    my_socket.connect(('127.0.0.1', 5555))
    player.verify()
    username = player.username
    player.wager_screen()
    wager = player.getWager()
    if player.Request == "play":
        start_time = time.time()
        BigCoinChange = 0
        while 1:
            if player.RecievedData == False:
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
                            # my_socket.send(str(Time_Counter).encode())
                            my_socket.close()
                            running = False
                    if event.type == QUIT:
                        my_socket.send(str(0).encode())
                        time.sleep(0.05)
                        # my_socket.send(str(Time_Counter).encode())
                        my_socket.close()
                        pygame.quit()
                        sys.exit()
                rlist, slist, xlist = select.select([player.my_socket], [], [], 0.1)
                for s in rlist:
                    msg = s.recv(1024)
                    print("Data from server", msg)
                    msg = msg.decode()
                    player.RecievedData = True
                    player.make_Ghosts()
                    print(msg)
                    if msg == "You can start":
                        player.has_died = False
                        player.all_eaten = False
                        continue
                    if msg == "You have won the Entire game!!":
                        if player.has_died == True:
                            reward = math.floor(1.5 * wager)
                            balance = balance + reward
                            print("Your balance is now:", balance)  # ???????????? ???? ???? ?????? ???? ???? ??????????????
                        if player.all_eaten == True:
                            reward = math.floor(2.5 * wager)
                            balance = balance + reward
                            print("Your balance is now:", balance)  # ???????????? ???? ???????? ?????????? ??????????????
                        while 1:
                            for event in pygame.event.get():
                                if event.type == KEYDOWN:
                                    if event.key == K_ESCAPE:
                                        my_socket.send(str(0).encode())
                                        time.sleep(0.05)
                                        # my_socket.send(str(Time_Counter).encode())
                                        my_socket.close()
                                        running = False
                                if event.type == QUIT:
                                    my_socket.send(str(0).encode())
                                    time.sleep(0.05)
                                    # my_socket.send(str(Time_Counter).encode())
                                    my_socket.close()
                                    pygame.quit()
                                    sys.exit()
                            screen.fill((0, 0, 0))
                            back_img = pygame.image.load("end_background.jpg")
                            back_img = pygame.transform.scale(back_img, (width, length))
                            screen.blit(back_img, (0, 0))
                            Font = pygame.font.SysFont('arial black', int(1.5 * square))
                            text = Font.render(msg, True, (255, 0, 0))
                            textRect = text.get_rect()
                            textRect.center = (length / 2, width / 2)
                            screen.blit(text, textRect)
                            pygame.display.update()  # ?????????? ?????????? ???? ??????????
            else:
                BigCoinChange += 1
                player.Board(background, BigCoinChange)
                if BigCoinChange == 100:
                    BigCoinChange = 0
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            my_socket.send(str(-1).encode())
                            time.sleep(0.05)
                            # my_socket.send(str(Time_Counter).encode())
                            my_socket.close()
                            running = False
                        elif event.key == K_UP or event.key == K_w:
                            req = 'up'
                        elif event.key == K_RIGHT or event.key == K_d:
                            req = 'right'
                        elif event.key == K_LEFT or event.key == K_a:
                            req = 'left'
                        elif event.key == K_DOWN or event.key == K_s:
                            req = 'down'
                    if event.type == QUIT:
                        my_socket.send(str(-1).encode())
                        time.sleep(0.05)
                        # my_socket.send(str(Time_Counter).encode())
                        my_socket.close()
                        pygame.quit()
                        sys.exit()

                if req == 'up':
                    if (player.canMove(math.floor(pacman[0] - pacspeed), pacman[1]) and pacman[1] % 1.0 == 0):
                        direction = 'up'
                if req == 'right':
                    if (player.canMove(pacman[0], math.ceil(pacman[1] + pacspeed)) and pacman[0] % 1.0 == 0):
                        direction = 'right'
                if req == 'left':
                    if (player.canMove(pacman[0], math.floor(pacman[1] - pacspeed)) and pacman[0] % 1.0 == 0):
                        direction = 'left'
                if req == 'down':
                    if (player.canMove(math.ceil(pacman[0] + pacspeed), pacman[1]) and pacman[1] % 1.0 == 0):
                        direction = 'down'
                pacman[0], pacman[1] = player.move(direction, pacman[0], pacman[1])
                if pacman[1] < 0.015625 and direction == 'left':
                    pacman[0], pacman[1] = player.move(direction, pacman[0], 27.484375)
                if pacman[1] > 26.984375 and direction == 'right':
                    pacman[0], pacman[1] = player.move(direction, pacman[0], 0.015625)
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
                    player.bigCoinEaten()
                    eatGhosts = True
                    blueCounter = 0
                for gh in player.ghosts:
                    died = gh.ifTouched()
                    if died == 'died':
                        player.died_wait()  # ???? ????????
                        screen.fill((0, 0, 0))  # ?????????? ???????? ?????????? ???????? ??died_wait
                        back_img = pygame.image.load("end_background.jpg")
                        back_img = pygame.transform.scale(back_img, (width, length))
                        screen.blit(back_img, (0, 0))
                        pygame.display.update()
                        password = player.password
                        username = player.username
                        signing = "log in"
                        if player.nextGame:  # ???? ????????
                            rlist, slist, xlist = select.select([player.my_socket], [], [], 0.1)
                            for s in rlist:
                                msg = s.recv(1024).decode()
                                print(msg)
                                player.nextGame = False
                        if player.nowSpectator==True:
                            player.wager_screen()
                            my_socket = socket.socket()
                            my_socket.connect(('127.0.0.1', 5555))
                            player.set_My_socket(my_socket)
                            data_to_send = (signing, username, password)
                            my_socket.send(pickle.dumps(data_to_send))
                            confirmation = my_socket.recv(1024)
                            my_socket.send("spectate".encode())
                            player.Queue_Again = False
                        if player.Queue_Again:  # ???? ?????????? ?????????? ???????? ?????????? ??????
                            player.wager_screen()
                            my_socket = socket.socket()
                            my_socket.connect(('127.0.0.1', 5555))
                            player.set_My_socket(my_socket)
                            data_to_send = (signing, username, password)
                            my_socket.send(pickle.dumps(data_to_send))
                            confirmation = my_socket.recv(1024)
                            print(confirmation)
                            my_socket.send("play".encode())
                            player.Queue_Again = False

                        if player.win:
                            print("I HAVE WON! BUT AT WHAT COST?!")
                            my_socket.send("go".encode())
                            print("sent message")
                            player.Intro_Render()
                        pacman = [23, 13.5]
                        direction = 'up'
                        coinCount = 0
                        req = 'up'
                        blueCounter = 0
                        eatGhosts = False
                        mouthChange = 0
                        BigCoinChange = 0
                        balance = player.balance
                        gameBoard = [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0,
                             0, ],
                            [0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 5, 5, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 4, 4, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 3, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0,
                             0, ],
                            [0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0,
                             0, ],
                            [0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                             0, ],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
                             0, ],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, ]
                        ]
                        player = PacMan(my_socket, direction, gameBoard, square, screen, pacman, coinCount, length,
                                        width,
                                        pacspeed, eatGhosts, mouthChange, player.wager, balance, True, False, username,
                                        password)
                        player.RecievedData = False
                    if died == 'eaten':
                        gh.eatenBlue()
                        coinCount += 400
                        eat_ghost = mixer.Sound('Sounds\pacman_eatghost.wav')
                        eat_ghost.set_volume(0.6)
                        eat_ghost.play()
                if eatGhosts:
                    if blueCounter == 3000:
                        for gh in player.ghosts:
                            gh.blueOver()
                        blueCounter = 0
                        eatGhosts = False
                    if blueCounter >= 2200 and blueCounter % 160 == 0:
                        for gh in player.ghosts:
                            if gh.getDied() == False:
                                gh.flickerToBLUE()
                    if blueCounter >= 2200 and blueCounter % 160 == 80:
                        for gh in player.ghosts:
                            gh.flickerToOG()
                    blueCounter += 1
                player.setPacMan(pacman)
                player.setCoinCount(coinCount)
                player.setDirection(direction)
                player.setEatGhosts(eatGhosts)
    else:
        player.spectate()


if __name__ == '__main__':
    main()
