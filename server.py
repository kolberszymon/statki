import socket
from _thread import *
import sys

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = '127.0.0.1'
PORT = 64000

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

server_socket.listen(2)
print("Waiting for connection")

currentId = 0

current_player_width = 0
current_player_height = 0

GAME_PHASES = [0, 0]
active_player_num = 1
checking_move = 0
global_action_num = 0

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
                arr = reply.split(":")
                player_num = int(arr[0])
                game_phase = int(arr[1])
                action_num = int(arr[2])
                width_pos = int(arr[3])
                height_pos = int(arr[4])

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
                        reply = f'{active_player_num}:{game_phase}:{action_num}:{current_player_width}:{current_player_height}'

                    #Aktywny gracz sie rusza
                    if action_num == 0:
                        current_player_width = width_pos
                        current_player_height = height_pos
                        reply = f'{active_player_num}:{game_phase}:{action_num}:{current_player_width}:{current_player_height}'

                    #Aktywny gracz naciska enter
                    if action_num == 1:
                        active_player_num = 1 - active_player_num
                        print("NEW ACTIVE PLAYER NEW ACTIVE PLAYER: " + str(active_player_num))
                        action_num = 1

                        reply = f'{active_player_num}:{game_phase}:{action_num}:{current_player_width}:{current_player_height}'

                elif game_phase == 4:
                    pass


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
