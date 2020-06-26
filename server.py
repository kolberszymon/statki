import argparse
import socket
from _thread import *
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-ip', help='Adres IP serwera (domyślnie 127.0.0.1)', type=str, default='127.0.0.1', required=False)
parser.add_argument('-p', '--port', help='Port serwera (domyślnie 64000)', type=int, default=64000, required=False)

args = parser.parse_args()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = args.ip
PORT = args.port


#FORMAT
#PLAYER_ID:GAME_PHASE:ACTION:POSITION_WIDTH:POSITION_HEIGHT
# ACTIONS:
# -1 to receive
# 0 MOVE
# 1 ENTER
# 2 Shot Succesful
# 3 shot missed

try:
    server_socket.bind((HOST, PORT))
except socket.error as e:
    print(str(e))

server_socket.listen(5)
print("Waiting for connection")

currentId = 0

current_player_width = 0
current_player_height = 0

GAME_PHASES = [0, 0]
active_player_num = 1
checking_move = 0
global_action_num = 0
LOSER_ID = 0

player1_ship_array = []
player2_ship_array = []

def threaded_client(conn):
    global currentId, border_position, current_player_width, current_player_height, active_player_num, checking_move, global_action_num
    is_starting = 1
    start_string = f'{currentId - 1}:{is_starting}'
    conn.send(str.encode(start_string))
    reply = ''

    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                print("Received: " + reply)
                if ":" in reply:
                    arr = reply.split(":")
                    player_num = int(arr[0])
                    game_phase = int(arr[1])
                    action_num = int(arr[2])
                    width_pos = int(arr[3])
                    height_pos = int(arr[4])
                else:
                    game_phase = 2
                    ships_coords = reply.split(" ")
                    player_num = int(ships_coords.pop())
                    ships = []
                    print(ships_coords)
                    print(len(ships_coords))

                    for ship in range(0, int(len(ships_coords) / 2)):
                        ship_coords = []
                        for i in range(0,2):
                            ship_coords.append(ships_coords.pop(0))

                        ship_coords[0] = int(ship_coords[0])
                        ship_coords[1] = int(ship_coords[1])

                        if player_num == 0:
                            if ship_coords not in player1_ship_array:
                                player1_ship_array.append(ship_coords)
                        else:
                            if ship_coords not in player2_ship_array:
                                player2_ship_array.append(ship_coords)


                if game_phase == 1:
                    GAME_PHASES[player_num] = game_phase
                    reply = f'{player_num}:{game_phase}'

                elif game_phase == 2:
                    if GAME_PHASES[player_num] == 1:
                        GAME_PHASES[player_num] = game_phase
                    if GAME_PHASES[0] == 2 and GAME_PHASES[1] == 2:
                        GAME_PHASES[0] = 3
                        GAME_PHASES[1] = 3
                    reply = f'{player_num}:{GAME_PHASES[player_num]}'

                elif game_phase == 3:

                    if action_num == -1:
                        reply = f'{active_player_num}:{GAME_PHASES[player_num]}:{action_num}:{current_player_width}:{current_player_height}'

                    #Aktywny gracz sie rusza
                    if action_num == 0:
                        current_player_width = width_pos
                        current_player_height = height_pos
                        reply = f'{active_player_num}:{game_phase}:{action_num}:{current_player_width}:{current_player_height}'

                    #Aktywny gracz naciska enter
                    if action_num == 1:
                        inactive_player_num = active_player_num
                        active_player_num = 1 - active_player_num
                        print("NEW ACTIVE PLAYER NEW ACTIVE PLAYER: " + str(active_player_num))
                        action_num = 1

                        if_shot_hit = 0

                        print([width_pos, height_pos])
                        print(f'player2shiparray: {player2_ship_array}')
                        print(f'player1shiparray:{player1_ship_array}')

                        if inactive_player_num == 0:
                            if [width_pos, height_pos] in player2_ship_array:
                                if_shot_hit = 1
                        elif inactive_player_num == 1:
                            if [width_pos, height_pos] in player1_ship_array:
                                if_shot_hit = 1

                        print(inactive_player_num)
                        print(f'{if_shot_hit} KAOKOFKOKFAKOFKAOSKFOASKFOKASOFKAOSKFOAKSFOKASOFKOAKSFOKASOFKOASKFOASKFOKAS')

                        reply = f'{active_player_num}:{game_phase}:{action_num}:{current_player_width}:{current_player_height}:{if_shot_hit}'

                    if action_num == 4:
                        GAME_PHASES[0] = 4
                        GAME_PHASES[1] = 4
                        game_phase = 4

                        reply = f'{player_num}:{4}'

                elif game_phase == 4:
                    print("444444444444445454545454")
                    LOSER_ID = player_num
                    reply = f'{LOSER_ID}:{4}'


                print("Sending: " + reply)

            conn.sendall(str.encode(reply))
        except socket.error as e:
            print(e)
            break

    print("Connection closed")
    currentId -= 1
    conn.close()

while True:
    conn, addr = server_socket.accept()
    print("Connected to: ", addr)
    currentId += 1

    start_new_thread(threaded_client, (conn,))
