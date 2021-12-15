import socket
from _thread import *
import sys

server = ""
port = 6969

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Server online, waiting for client connections...")

def threaded_client(conn):
    reply = ""
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")

            if not data:
                print("Client disconnected")
                break
            else:
                print("Recieved {}".format(reply))
            conn.sendall(str.encode(reply))
        except:
            print("Data reception error, diconnected")
            break

while True:
    conn, addr = s.accept()
    print("Connected to {}".format(addr))

    start_new_thread(threaded_client, (conn))
