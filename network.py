import socket

class Network:

    host = ''
    port = 0

    def __init__(self, ip, p):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = ip
        self.port = p
        self.addr = (self.host, self.port)
        self.id, self.is_player_active = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        data = self.client.recv(2048).decode()
        id, is_player_active = data.split(":")
        return int(id), int(is_player_active)

    def send(self, data):


        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)
