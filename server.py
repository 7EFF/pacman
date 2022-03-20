import socket
import select

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

print("Setting up server...")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()
print("Listening for clients...")
client_sockets = []
Coins_Results=[]
Times_Results=[]

def main():
    while True:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                client_sockets.append(connection)
            else:
                Result_Coins=current_socket.recv(MAX_MSG_LENGTH).decode()  # כמה מטבעות קיבל הלקוח
                if Result_Coins!=0:
                    Coins_Results[current_socket] = Result_Coins
                Result_Time=current_socket.recv(MAX_MSG_LENGTH).decode() #כמה זמן סיים הלקוח
                if Result_Time != 0:
                    Times_Results[current_socket]=Result_Time

if __name__ == '__main__':
    main()