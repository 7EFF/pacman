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
Coins_Results = {}
Times_Results = {}
Recieved_Clients = {}


class server:
    def __init__(self, client_sockets, current_socket, Coins_Results, Times_Results):
        self.client_sockets = client_sockets
        self.current_socket = current_socket
        self.Coins_Results = Coins_Results
        self.Times_Results = Times_Results

    def print_client_sockets(self):
        for c in self.client_sockets:
            print(c.getpeername())

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
    while True:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                client_sockets.append(connection)
                Recieved_Clients[connection] = False

            else:
                Result_Coins = current_socket.recv(MAX_MSG_LENGTH).decode()  # כמה מטבעות קיבל הלקוח

                if Result_Coins == 0:
                    client_sockets.remove(current_socket)
                    current_socket.close()
                    continue
                else:
                    Coins_Results[current_socket] = Result_Coins
                    print(Result_Coins, "Coins")
                Result_Time = current_socket.recv(MAX_MSG_LENGTH).decode()  # כמה זמן סיים הלקוח
                Recieved_Clients[current_socket] = True
                Times_Results[current_socket] = Result_Time
                print(Result_Time, "Time")
                Game = server(client_sockets, current_socket, Coins_Results, Times_Results)
                if not False in Recieved_Clients.values():
                    print('bulbul')
                    Game.checkWinner()
                    break


if __name__ == '__main__':
    main()
