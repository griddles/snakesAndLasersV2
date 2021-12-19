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
    
    def getPlayer(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048 * 4))
        except:
            pass
    
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048 * 4))
        except socket.error as e:
            print(e)
