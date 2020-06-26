import game_update
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', help='Adres IP serwera', type=str)
    parser.add_argument('-p', '--port', help='Port serwera', type=int)

    args = parser.parse_args()
    g = game_update.Game(args.ip, args.port)
    g.run()
