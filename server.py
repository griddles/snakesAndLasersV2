import socket
from _thread import *
import sys
import game

server = "192.168.208.45"
port = 6969

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Server online, waiting for client connections...")

players = [game.HeadRect(427, 240), game.HeadRect(853, 480)]

def threaded_client(conn, player):
    global currentPlayer
    conn.send(str.encode(writePos(pos[player])))
    reply = ""
    while True:
        try:
            data = readPos(conn.recv(2048).decode())
            pos[player] = data

            if not data:
                print("Client disconnected")
                break
            else:
                reply = pos[0] if player == 1 else pos[1]
                print("Recieved \"{}\"".format(data))
                print("Sending \"{}\"".format(reply))
            conn.sendall(str.encode(writePos(reply)))
        except:
            break
    print("Lost connection")
    currentPlayer -= 1
    conn.close()

currentPlayer = 0

while True:
    conn, addr = s.accept()
    print("Connected to {}".format(addr))

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
