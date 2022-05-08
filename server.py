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

    def __init__(self, client_sockets, current_socket, Coins_Results, Times_Results, Recieved_Clients):
        self.client_sockets = client_sockets
        self.current_socket = current_socket
        self.Coins_Results = Coins_Results
        self.Times_Results = Times_Results
        self.Recieved_Clients=Recieved_Clients

    def get_Recieved_Clients(self):
        return self.Recieved_Clients

    def print_client_sockets(self):
        for c in self.client_sockets:
            print(c.getpeername())

    def Game(self):
        for c in self.client_sockets:
            data_from_client = pickle.loads(c.recv(2048))# מקבל את המטבעות ואת הזמן של הלקוח
            Result_Coins, Result_Time=data_from_client
            if Result_Coins == -1:
                client_sockets.remove(c)
                c.close()
                continue
            else:
                Coins_Results[c] = Result_Coins
                print(Result_Coins, "Coins")
            Times_Results[c] = Result_Time
            print(Result_Time, "Time")
            self.Recieved_Clients[c] = True #מסמן שאותו לקוח שלח את כל מה שהיה צריך לשלוח
        return

    def checkWinner(self):
        maxCoins = 0
        maxCoinsClient = ""
        winner = ""
        switchToTime = False
        for i in client_sockets:
            if int(Coins_Results[i]) > maxCoins:
                maxCoins = int(Coins_Results[i])
                maxCoinsClient = i
                switchToTime = False
                winner = i
            if Coins_Results[i] == maxCoins:
                switchToTime = True
        print(maxCoins, "Max Coins")
        if switchToTime:
            minTime = 0
            minTimeClient = ""
            for i in client_sockets:
                if int(Times_Results[i]) < minTime:
                    minTime = Times_Results[i]
                    minTimeClient = i
                print(minTime)
                winner = i

        for c in client_sockets:
            if c == winner:
                msg = "You have won !"
                c.send(msg.encode())
            else:
                msg = "You have lost"
                c.send(msg.encode())


def main():
    Recieved_Clients = {}
    Number_Clients=0
    Waiting_Room=[]
    while 1:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                Request = connection.recv(MAX_MSG_LENGTH).decode()#מקבל את הבקשה מאחד הלקוחות. שחקן, צופה או לשחק עוד הפעם
                if Request=="go":
                    client_sockets.append(connection)
                    Waiting_Room.append(connection)
                    Recieved_Clients[connection] = False
                    if len(Waiting_Room) == 2:
                        Lobby = server(Waiting_Room, current_socket, Coins_Results, Times_Results,Recieved_Clients)#יוצר את המשחק הכללי
                        for c in Waiting_Room:
                            msg = "You can start"
                            c.send(msg.encode()) #שולח לכל שחקן שהוא יכול להתחיל לשחק
                        x = threading.Thread(target=Lobby.Game()) #יוצר משחק בין שני אנשים
                        x.start()
                        Waiting_Room.clear()
                        x.join()
                        #print(Lobby.Recieved_Clients.values())
                        if not False in Lobby.Recieved_Clients.values():
                            Lobby.checkWinner()#בודק מי ניצח באחד המשחקים


if __name__ == '__main__':
    main()
