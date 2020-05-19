import socket
from game import *
import threading
import time

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'

DISCONNECT_MESSAGE = "!DISCONNECT"
READY_MESSAGE = "!READY"

READY = False

SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
CONNECTED = False

def start_connection():
    global CONNECTED
    time.sleep(2)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(ADDR)
        CONNECTED = True
    except socket.error as e:
        print(str(e))


    network.update_connected_status(CONNECTED)


    def send(msg):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)
        print(client.recv(2048).decode(FORMAT))

    while CONNECTED:
        global READY
        while not READY:
            time.sleep(1)
            send("1")
            message = client.recv(128)
            if message == READY_MESSAGE:
                READY = True
        while READY:
            send("2")
            message = client.recv(128)
            print(str(message))

    input("Wait")
    send(DISCONNECT_MESSAGE)

def start_thread_with_connection():
    thread = threading.Thread(target=start_connection)
    thread.start()

start_thread_with_connection()
start_game()
