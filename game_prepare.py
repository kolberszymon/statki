### Connecting to server
### Waiting for the other player

from network import Network

class Game():

    def __init__(self):
        self.net = Network()

    def run(self):
        while True:

            reply = self.parse_data(self.send_data())

    def send_data(self):
        data = "0:0:0:0"
        reply = self.net.send(data)
        print(reply)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")
            print(d)
            return int(d[0]), int(d[1]), int(d[2]), int(d[3])
        except:
            return 0,0,0,0

game = Game()
game.run()
