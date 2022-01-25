"""
Snakes and Lasers v2.1.1 Network Handler
Handles network interaction on the client side.
"""

import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = open(r"ipAddress.txt", "r")
        ip.seek(0)
        self.server = ip.read()
        self.port = 6969
        self.addr = (self.server, self.port)
        self.p = self.connect()
    
    # when the client wants to get their player object, return the first value the server sent to this object.
    def getPlayer(self):
        return self.p

    # connect to the server and return the first data value the server sends
    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass
    
    # send data to the server, and return the data we get back.
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)
