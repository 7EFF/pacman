import socket
import select
import time

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

print("Setting up server...")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()
print("Listening for clients...")
client_sockets = []
Coins_Results={}
Times_Results={}

class server:
    def __init__(self,client_sockets,current_socket,Coins_Results,Times_Results):
        self.client_sockets = client_sockets
        self.current_socket = current_socket
        self.Coins_Results=Coins_Results
        self.Times_Results=Times_Results

    def checkWinner(self):
        maxCoins=0
        maxCoinsClient=""
        switchToTime=False
        for i in client_sockets:
            if Coins_Results[i]>maxCoins:
                maxCoins=Coins_Results[i]
                maxCoinsClient=i
                switchToTime = False
            if Coins_Results[i]==maxCoins:
                switchToTime=True
        print(maxCoins)
        if switchToTime:
            maxTime=0
            maxCoinsTime=""
            for i in client_sockets:
                if Times_Results[i] > maxCoins:
                    maxTime = Times_Results[i]
                    maxCoinsTime = i
                print(maxTime)

def main():
    while True:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                client_sockets.append(connection)
            else:
                Result_Coins=current_socket.recv(MAX_MSG_LENGTH).decode() # כמה מטבעות קיבל הלקוח
                if Result_Coins==" ":
                    client_sockets.remove(current_socket)
                    current_socket.close()
                    continue
                else:
                    Coins_Results[current_socket] = Result_Coins
                    print(Result_Coins, "Coins")
                Result_Time=current_socket.recv(MAX_MSG_LENGTH).decode() #כמה זמן סיים הלקוח
                if Result_Time == "":
                    client_sockets.remove(current_socket)
                    current_socket.close()
                    continue
                else:
                    Times_Results[current_socket] = Result_Time
                    print(Result_Time, "Time")
                Game = server(client_sockets, current_socket, Coins_Results,Times_Results)
                Game.checkWinner()

if __name__ == '__main__':
    main()
