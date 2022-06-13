import socket
import select
import time
import threading
import pickle

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


class server:

    def __init__(self, client_sockets, current_socket, Recieved_Clients):
        self.client_sockets = client_sockets
        self.current_socket = current_socket
        self.Coins_Results = {}
        self.Times_Results = {}
        self.Recieved_Clients=Recieved_Clients
        self.QueueAgain=[]
        self.winners_list=[]

    def get_Recieved_Clients(self):
        return self.Recieved_Clients

    def get_winners_list(self):
        return self.winners_list

    def set_Game_list(self,Game_list):
        self.client_sockets=Game_list

    def print_client_sockets(self):
        for c in self.client_sockets:
            print(c.getpeername())

    def get_QueueAgain(self):
        return self.QueueAgain

    def Game(self):
        for c in self.client_sockets:
            data_from_client = pickle.loads(c.recv(2048))# מקבל את המטבעות ואת הזמן של הלקוח
            Result_Coins, Result_Time=data_from_client
            if Result_Coins == -1:
                client_sockets.remove(c)
                c.close()
                continue
            self.Coins_Results[c] = Result_Coins
            print(Result_Coins, "Coins")
            self.Times_Results[c] = Result_Time
            print(Result_Time, "Time")
            self.Recieved_Clients[c] = True #מסמן שאותו לקוח שלח את כל מה שהיה צריך לשלוח
        self.checkWinner()  # בודק מי ניצח באחד המשחקים
        return

    def checkWinner(self):
        maxCoins = 0
        minTime=0
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
        losers_list =[]
        for c in self.client_sockets:
            if c == winner:
                msg = "You have won this duel!"
                c.send(msg.encode())
                self.winners_list.append(c)
                if all(self.Recieved_Clients.values())==True:
                    self.checkIfGameOver()
            else:
                msg = "You have lost"
                c.send(msg.encode())
                losers_list.append(c)
        for L in losers_list:
            req = L.recv(1024).decode()
            print(req)
            losers_list.remove(L)

    def checkIfGameOver(self):
        if len(self.winners_list)==1:
            msg = "You have won this game!!"
            self.winners_list[0].send(msg.encode())
        else:
            for c in self.winners_list:
                msg = "You will fight the other winner soon"
                c.send(msg.encode())


def main():
    Recieved_Clients = {}
    Number_Clients=0
    Waiting_Room=[]
    Game_list=[]
    while 1:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                Request = connection.recv(MAX_MSG_LENGTH).decode()  # מקבל את הבקשה מאחד הלקוחות. שחקן, צופה או לשחק עוד הפעם
                if Request=="go":
                    client_sockets.append(connection)
                    Waiting_Room.append(connection)
                    Recieved_Clients[connection] = False
                    Lobby = server(client_sockets, current_socket, Recieved_Clients)  # יוצר את המשחק הכללי
                    if len(Waiting_Room) >= 2:
                        for c in Waiting_Room:
                            msg = "You can start"
                            c.send(msg.encode()) #שולח לכל שחקן שהוא יכול להתחיל לשחק
                        Players=int(len(Waiting_Room)/2)
                        for i in range(Players):
                            Game_list = Waiting_Room[0],Waiting_Room[1]
                            Lobby.set_Game_list(Game_list)
                            x = threading.Thread(target=Lobby.Game) #יוצר משחק בין שני אנשים
                            x.start()
                            Waiting_Room.remove(Waiting_Room[1])
                            Waiting_Room.remove(Waiting_Room[0])
                        Lobby.checkIfGameOver()



if __name__ == '__main__':
    main()
