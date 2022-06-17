import math
import socket
import select
import time
import threading
import pickle
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

key = ""

engine = create_engine('mysql://root:Jt202004@localhost:3306/players_data', echo=False)

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Users(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    password = Column(String(50))
    balance = Column(Integer)
    games_played = Column(Integer)
    games_won = Column(Integer)

    def __init__(self, name, password, balance, games_played, games_won):
        self.name = name
        self.password = password
        self.balance = balance
        self.games_played = games_played
        self.games_won = games_won

    def changeBalance(self, win, wager, username, eaten_all):
        user = session.query(Users).filter(Users.name == username).first()
        if win == False and eaten_all == False:
            user.balance = user.balance - wager
        if win == True and eaten_all == False:
            user.balance = user.balance + wager
        if win == False and eaten_all == True:
            user.balance = user.balance + math.floor(2.5 * wager)
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
                    if user.password == password:
                        msg = "Welcome back " + username
                        balance = user.balance
                        data_to_send = (msg, balance)
                        connection.send(pickle.dumps(data_to_send))
                        running = False
                        return
                    else:
                        msg = "Incorrect password or name"
                        balance = 0
                        data_to_send = (msg, balance)
                        connection.send(pickle.dumps(data_to_send))
                        data_from_client = pickle.loads(connection.recv(2048))  # מקבל את הסיסמה, השם והסוג כניסה של המשתמש
                        signing, username, password = data_from_client
                else:
                    msg = "Incorrect password or name"
                    balance = 0
                    data_to_send = (msg, balance)
                    connection.send(pickle.dumps(data_to_send))
                    data_from_client = pickle.loads(connection.recv(2048))  # מקבל את הסיסמה, השם והסוג כניסה של המשתמש
                    signing, username, password = data_from_client
        if signing=="sign up":
            running = True
            namesList = Users.getNamesList(self)
            while running == True:
                if username not in namesList:
                    user = Users(name=username, password=password, balance=1000, games_played=0, games_won=0)
                    session.add(user)
                    session.commit()
                    msg = "Welcome to PacMn"
                    balance=1000
                    data_to_send = (msg, balance)
                    connection.send(pickle.dumps(data_to_send))
                    running=False
                    return
                else:
                    msg = "Name already exists"
                    balance = 0
                    data_to_send = (msg, balance)
                    connection.send(pickle.dumps(data_to_send))
                    data_from_client = pickle.loads(connection.recv(2048))  # מקבל את הסיסמה, השם והסוג כניסה של המשתמש
                    signing, username, password = data_from_client

users = session.query(Users)
for user in users:
    print(user.id, user.name, user.password, user.balance)

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

print("Setting up server...")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()
print("Listening for clients...")
client_sockets = []
Coins_Results = {}
Times_Results = {}
winners_list = []


class server:

    def __init__(self, client_sockets, current_socket, Recieved_Clients):
        self.client_sockets = client_sockets
        self.current_socket = current_socket
        self.Coins_Results = {}
        self.Times_Results = {}
        self.Recieved_Clients = Recieved_Clients
        self.QueueAgain = []

    def get_Recieved_Clients(self):
        return self.Recieved_Clients

    def set_Game_list(self, Game_list):
        self.client_sockets = Game_list

    def print_client_sockets(self):
        for c in self.client_sockets:
            print(c.getpeername())

    def get_QueueAgain(self):
        return self.QueueAgain

    def Game(self):
        winners_list = []
        for c in self.client_sockets:
            data_from_client = pickle.loads(c.recv(2048))  # מקבל את המטבעות ואת הזמן של הלקוח
            Result_Coins, Result_Time, wager, username, eaten_all = data_from_client
            if Result_Coins == -1:
                client_sockets.remove(c)
                del self.Recieved_Clients[c]
                c.close()
                continue
            self.Coins_Results[c] = Result_Coins
            print(Result_Coins, "Coins")
            self.Times_Results[c] = Result_Time
            print(Result_Time, "Time")
            self.Recieved_Clients[c] = True  # מסמן שאותו לקוח שלח את כל מה שהיה צריך לשלוח
        self.checkWinner(wager, username, eaten_all)  # בודק מי ניצח באחד המשחקים

    def checkWinner(self, wager, username, eaten_all):
        maxCoins = 0
        minTime = 0
        maxCoinsClient = ""
        winner = ""
        switchToTime = False
        for i in self.client_sockets:
            if self.Coins_Results[i] == maxCoins:
                switchToTime = True
            if int(self.Coins_Results[i]) > maxCoins:
                maxCoins = int(self.Coins_Results[i])
                maxCoinsClient = i
                switchToTime = False
                winner = i
        print(maxCoins, "Max Coins")
        if switchToTime:
            minTime = 0
            minTimeClient = ""
            for i in self.client_sockets:
                if int(self.Times_Results[i]) < minTime:
                    minTime = self.Times_Results[i]
                    minTimeClient = i
                    winner = i
        print(minTime, "Min Time")
        losers_list = []
        for c in self.client_sockets:
            if c != winner:
                Users.changeBalance(user, False, wager, username, eaten_all)
                msg = "You have lost"
                c.send(msg.encode())
                losers_list.append(c)
            else:
                Users.changeBalance(user, True, wager, username, eaten_all)
                msg = "You have won this duel!"
                c.send(msg.encode())
                winners_list.append(c)
        if all(self.Recieved_Clients.values()) == True:
            self.set_Game_list([])
            for connection in winners_list:
                msg = connection.recv(1024).decode()
                time.sleep(0.05)
                if msg == "go":
                    self.client_sockets.append(connection)
                    self.Recieved_Clients[connection] = False
            if len(self.client_sockets) == 2:
                for c in self.client_sockets:
                    msg = "You can start"
                    c.send(msg.encode())  # שולח לכל שחקן שהוא יכול להתחיל לשחק
                    winners_list.remove(c)
                self.Game()
            if len(self.client_sockets) == 1:
                msg = "You have won the Entire game!!"
                self.client_sockets[0].send(msg.encode())
                winners_list.remove(self.client_sockets[0])
        for L in losers_list:
            req = L.recv(1024).decode()
            print(req)
            losers_list.remove(L)
            del self.Recieved_Clients[L]

def main():
    Recieved_Clients = {}
    Number_Clients = 0
    Waiting_Room = []
    Game_list = []
    while True:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [],0.1)
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                client_sockets.append(connection)
                data_from_client = pickle.loads(connection.recv(2048))  # מקבל את הסיסמה, השם והסוג כניסה של המשתמש
                signing, username, password = data_from_client
                Users.signing(user, signing, username, password, connection)
            else:
                Request = current_socket.recv(MAX_MSG_LENGTH).decode()  # מקבל את הבקשה מאחד הלקוחות. שחקן, צופה או לשחק עוד הפעם
                print(Request)
                if Request == "go":
                    client_sockets.append(current_socket)
                    Waiting_Room.append(current_socket)
                    Recieved_Clients[current_socket] = False
                    Lobby = server(client_sockets, current_socket, Recieved_Clients)  # יוצר את המשחק הכללי
                    x = threading.Thread(target=Lobby.Game)  # יוצר משחק בין שני אנשים
                    if len(Waiting_Room) >= 2:
                        for c in Waiting_Room:
                            msg = "You can start"
                            c.send(msg.encode())  # שולח לכל שחקן שהוא יכול להתחיל לשחק
                        Players = int(len(Waiting_Room) / 2)
                        for i in range(Players):
                            Game_list = Waiting_Room[0], Waiting_Room[1]
                            Lobby.set_Game_list(Game_list)
                            x.start()
                            Waiting_Room.remove(Waiting_Room[1])
                            Waiting_Room.remove(Waiting_Room[0])


if __name__ == '__main__':
    main()
