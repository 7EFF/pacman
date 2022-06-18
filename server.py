import math
import socket
import select
import time
import threading
import pickle
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List

key = ""

engine = create_engine('mysql://root:Jt202004@localhost:3306/players_data', echo=False)

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Globals
In_game = []
client_sockets = []
Coins_Results = {}
Times_Results = {}
bet_on = {}
winners_list = []


class Users(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    password = Column(String(50))
    balance = Column(Integer)
    games_played = Column(Integer)
    games_won = Column(Integer)
    online = Column(Boolean)

    def __init__(self, name, password, balance, games_played, games_won, online):
        self.name = name
        self.password = password
        self.balance = balance
        self.games_played = games_played
        self.games_won = games_won
        self.online = online

    def changeBalance(self, win, wager, username, eaten_all):
        user = session.query(Users).filter(Users.name == username).first()
        if win == False and eaten_all == False:
            user.balance = user.balance - wager
        if win == True and eaten_all == False:
            user.games_won += 1
            user.balance = user.balance + math.floor(wager * 1.5)
        if win == True and eaten_all == True:
            user.games_won += 1
            user.balance = user.balance + math.floor(2.5 * wager)
        #print(user.balance, "is what", username, " now has")
        user.games_played += 1
        user.online = False
        session.commit()
        return

    def getNamesList(self):
        namesList = []
        users = session.query(Users)
        for user in users:
            namesList.append(user.name)
        return namesList

    def signing(self, signing, username, password, connection):
        if signing == "log in":
            running = True
            namesList = Users.getNamesList(self)
            while running == True:
                if username in namesList:
                    user = session.query(Users).filter(Users.name == username).first()
                    if user.password == password and user.online == False:
                        msg = "Welcome back " + username
                        balance = user.balance
                        data_to_send = (msg, balance)
                        connection.send(pickle.dumps(data_to_send))
                        user.online = True
                        running = False
                    else:
                        msg = "Incorrect password or name"
                        balance = 0
                        data_to_send = (msg, balance)
                        connection.send(pickle.dumps(data_to_send))
                        data_from_client = pickle.loads(
                            connection.recv(2048))  # מקבל את הסיסמה, השם והסוג כניסה של המשתמש
                        signing, username, password = data_from_client
                else:
                    msg = "Incorrect password or name"
                    balance = 0
                    data_to_send = (msg, balance)
                    connection.send(pickle.dumps(data_to_send))
                    data_from_client = pickle.loads(connection.recv(2048))  # מקבל את הסיסמה, השם והסוג כניסה של המשתמש
                    signing, username, password = data_from_client
            return
        if signing == "sign up":
            running = True
            namesList = Users.getNamesList(self)
            while running == True:
                if username not in namesList:
                    user = Users(name=username, password=password, balance=1000, games_played=0, games_won=0,
                                 online=True)
                    session.add(user)
                    session.commit()
                    msg = "Welcome to PacMn"
                    balance = 1000
                    data_to_send = (msg, balance)
                    connection.send(pickle.dumps(data_to_send))
                    running = False
                else:
                    msg = "Name already exists"
                    balance = 0
                    data_to_send = (msg, balance)
                    connection.send(pickle.dumps(data_to_send))
                    data_from_client = pickle.loads(connection.recv(2048))  # מקבל את הסיסמה, השם והסוג כניסה של המשתמש
                    signing, username, password = data_from_client
            return


users = session.query(Users)
for user in users:
    print(user.id, user.name, user.password, user.balance)
    user.online = False
    session.commit()

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

print("Setting up server...")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()
print("Listening for clients...")


class server:

    def __init__(self, Recieved_Clients):
        self.game_sockets = []
        self.Coins_Results = {}
        self.Times_Results = {}
        self.Recieved_Clients = Recieved_Clients
        self.QueueAgain = []
        self.spect_wagers = {}

    ##########################SETS & GETS##########################

    def get_Recieved_Clients(self):
        return self.Recieved_Clients

    def set_Game_list(self, Game_list):
        self.game_sockets = list(Game_list)

    def print_client_sockets(self):
        for c in self.game_sockets:
            print(c.getpeername())

    def get_QueueAgain(self):
        return self.QueueAgain

    ##########################SETS & GETS##########################

    ##########################DUAL##########################

    def Game(self):
        names_list = {}
        wagers_list = {}
        eaten_all_list = {}
        for c in self.game_sockets:
            data_from_client = pickle.loads(c.recv(2048))  # מקבל את המטבעות ואת הזמן של הלקוח
            Result_Coins, Result_Time, wager, username, eaten_all = data_from_client
            if Result_Coins == -1:
                client_sockets.remove(c)
                del self.Recieved_Clients[c]
                c.close()
                user = session.query(Users).filter(Users.name == username).first()
                user.online = False
                continue
            names_list[c] = username
            wagers_list[c] = wager
            eaten_all_list[c] = eaten_all
            self.Coins_Results[c] = Result_Coins
            #print(Result_Coins, "Coins ", username, " has gotten")
            self.Times_Results[c] = Result_Time
            #print(Result_Time, "Time", username, " has gotten")
            self.Recieved_Clients[c] = True  # מסמן שאותו לקוח שלח את כל מה שהיה צריך לשלוח
        self.checkWinner(wagers_list, names_list, eaten_all_list)  # בודק מי ניצח באחד המשחקים

    def checkWinner(self, wagers_list, names_list, eaten_all_list):
        global In_game
        maxCoins = 0
        minTime = 0
        maxCoinsClient = ""
        winner = ""
        switchToTime = False
        for i in self.game_sockets:
            if self.Coins_Results[i] == maxCoins:
                switchToTime = True
            if int(self.Coins_Results[i]) > maxCoins:
                maxCoins = int(self.Coins_Results[i])
                maxCoinsClient = i
                switchToTime = False
                winner = i
        print(maxCoins, "Max Coins")
        if switchToTime:
            minTime = 10000000
            minTimeClient = ""
            for i in self.game_sockets:
                if int(self.Times_Results[i]) <= minTime:
                    minTime = self.Times_Results[i]
                    minTimeClient = i
                    winner = i
        print(minTime, "Min Time")
        losers_list = []
        for c in self.game_sockets:
            if c != winner:
                Users.changeBalance(user, False, wagers_list[c], names_list[c], eaten_all_list[c])
                msg = "You have lost"
                c.send(msg.encode())
                client_sockets.remove(c)
                del self.Recieved_Clients[c]
                In_game.remove(c)
                print(bet_on)
                print(names_list)
                for connection in bet_on:
                    if bet_on[connection] == names_list[c]:
                        msg = "Your bet has lost"
                        connection.send(msg.encode())
            else:
                Users.changeBalance(user, True, wagers_list[c], names_list[c], eaten_all_list[c])
                print("SENDING WON THIS DUEL")
                msg = "You have won this duel!"
                c.send(msg.encode())
                winners_list.append(c)
                for connection in bet_on:
                    if bet_on[connection] == names_list[c]:
                        msg = "Your bet has won"
                        connection.send(msg.encode())

        ##### After game ended #####

        if all(self.Recieved_Clients.values()):
            self.set_Game_list([])
            for connection in winners_list:
                msg = connection.recv(1024).decode()
                time.sleep(0.05)
                if msg == "go":
                    self.game_sockets.append(connection)
                    self.Recieved_Clients[connection] = False
            if len(self.game_sockets) == 2:
                print("CLIENTS START NEW MATCH FINAL")
                for c in self.game_sockets:
                    msg = "You can start"
                    c.send(msg.encode())  # שולח לכל שחקן שהוא יכול להתחיל לשחק
                    winners_list.remove(c)
                self.Game()
                return
            if len(self.game_sockets) == 1:
                msg = "You have won the Entire game!!"
                self.game_sockets[0].send(msg.encode())
                if self.game_sockets[0] in winners_list:
                    winners_list.remove(self.game_sockets[0])

                c = self.game_sockets[0]
                client_sockets.remove(c)
                del self.Recieved_Clients[c]
                In_game.remove(c)
        else:
            return

    ##########################DUAL##########################

    ##########################SPECTATORS##########################

    def choose(self, spectators_list, users, connection):
        for user in users:
            if user.name not in spectators_list:
                data_to_send = (user.name, user.games_played, user.games_won)
                connection.send(pickle.dumps(data_to_send))
                print(user.name, user.games_played, user.games_won)
                data_from_client = pickle.loads(connection.recv(2048))  # מקבל את הסיסמה, השם והסוג כניסה של המשתמש
                Request, wager = data_from_client
                print(Request)
                if Request == "yes":
                    self.spect_wagers[connection] = wager
                    bet_on[connection] = user.name
                    print(self.spect_wagers)
                    print(bet_on)

                    break
        return

    def spectate(self, spectators_list):
        print(self.spect_wagers)
        print(bet_on)
        users = session.query(Users)
        for connection in spectators_list.values():
            x = threading.Thread(target=self.choose, args=(spectators_list, users, connection,), daemon=True)
            x.start()
        return

    ##########################SPECTATORS##########################


def main():
    global In_game
    spectators_list = {}
    Recieved_Clients = {}
    Number_Clients = 0
    Waiting_Room: List[socket.socket] = []
    Game_list = []
    signing = ""
    username = ""
    password = ""
    connection = ""
    user = ""
    addresses = {}
    while True:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [], 0.1)
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                client_sockets.append(connection)
                addresses[connection] = client_address
            else:
                if current_socket not in Waiting_Room and current_socket not in In_game:
                    ret = current_socket.recv(2048)
                    print(ret)
                    if not ret:
                        client_sockets.remove(current_socket)
                        continue
                    data_from_client = pickle.loads(ret)
                    print("got data", addresses[current_socket])
                    signing, username, password = data_from_client
                    Users.signing(user, signing, username, password, current_socket)
                    Request = current_socket.recv(
                        MAX_MSG_LENGTH).decode()  # מקבל את הבקשה מאחד הלקוחות. שחקן, צופה או לשחק עוד הפעם
                    print(signing, username, password, Request)
                    if Request == "play":
                        client_sockets.append(current_socket)
                        Waiting_Room.append(current_socket)
                        Recieved_Clients[current_socket] = False
                    if Request == "spectate":
                        spectators_list[username] = current_socket
                        Lobby = server(Recieved_Clients)  # יוצר את המשחק הכללי
                        x = threading.Thread(target=Lobby.spectate, args=(spectators_list,), daemon=True)
                        x.start()
        # search for 2 clients in waiting room

        if len(Waiting_Room) >= 2:
            sockets_to_game = Waiting_Room[:2]
            for c in sockets_to_game:
                msg = "You can start"
                c.send(msg.encode())  # שולח לכל שחקן שהוא יכול להתחיל לשחק
                Waiting_Room.remove(c)
                In_game.append(c)
            Game_list = sockets_to_game[0], sockets_to_game[1]
            lobby = server(Recieved_Clients)  # יוצר את המשחק הכללי
            x = threading.Thread(target=lobby.Game)  # יוצר משחק בין שני אנשים
            lobby.set_Game_list(Game_list)
            x.start()
            print("Started Game!")
            print([addresses[i] for i in sockets_to_game])

        time.sleep(0.1)


if __name__ == '__main__':
    main()
