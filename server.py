import socket
from _thread import *
import _pickle as pickle
import time
import random
import math

# setup sockets
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set constants
PORT = 5555

BALL_RADIUS = 5
START_RADIUS = 7
w = 30
h = 50
ROUND_TIME = 10

MASS_LOSS_TIME = 7

W, H = 1024, 600

HOST_NAME = socket.gethostname()
SERVER_IP = 'localhost'

maps = [[[200, 300, 200, 100], [500, 200, 300, 100]], [[800, 300, 500, 100], [500, 200, 300, 100]]]

# try to connect to server
try:
    S.bind((SERVER_IP, PORT))
except socket.error as e:
    print(str(e))
    print("[SERVER] Server could not start")
    quit()

S.listen()  # listen for connections

print(f"[SERVER] Server Started with local ip {SERVER_IP}")

players = {}
connections = 0
_id = 0
colors = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (128, 255, 0), (0, 255, 0), (0, 255, 128), (0, 255, 255),
          (0, 128, 255), (0, 0, 255), (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128), (128, 128, 128),
          (0, 0, 0)]
start = False
nxt = 1


def getMap():
    map = random.randint(0, 1)
    return map


def threaded_client(conn, _id):
    global connections, players, nxt, start, mapa, game_time, start_time

    if connections == 1:
        start_time = time.time()
        start = True
        map = getMap()
        mapa = maps[map]
    current_id = _id
    data = conn.recv(16)
    name = data.decode("utf-8")
    print("[LOG]", name, "connected to the server.")
    color = colors[current_id]
    x, y = 512, 300
    players[current_id] = {
        "x": x,
        "y": y,
        "color": color,
        "score": 0,
        "name": name,
        "left": False,
        "right": False,
        "lastkey": 'right',
        "w": w,
        "h": h
    }
    conn.send(str.encode(str(current_id)))

    while True:

        if start:
            game_time = round(time.time() - start_time)

            if game_time >= ROUND_TIME:
                start_time = time.time()
                map = getMap()
                mapa = maps[map]
                game_time = round(time.time() - start_time)

        try:
            data = conn.recv(32)

            if not data:
                break

            data = data.decode("utf-8")
            if data.split(" ")[0] == "move":
                split_data = data.split(" ")
                x = int(split_data[1])
                y = int(split_data[2])
                left = split_data[3]
                right = split_data[4]
                lastkey = split_data[5]
                players[current_id]["x"] = x
                players[current_id]["y"] = y
                players[current_id]["left"] = left
                players[current_id]["right"] = right
                if lastkey != '':
                    players[current_id]["lastkey"] = lastkey
                else:
                    pass
                send_data = pickle.dumps((players, game_time))
            elif data.split(" ")[0] == "map":
                send_data = pickle.dumps(mapa)
            else:
                # any other command just send back list of players
                send_data = pickle.dumps((players, game_time))

            # send data back to clients
            conn.send(send_data)

        except Exception as e:
            print(e)
            break

        time.sleep(0.001)


    print("[DISCONNECT] Name:", name, ", Client Id:", current_id, "disconnected")

    connections -= 1
    del players[current_id]
    conn.close()

print("[GAME] Setting up level")
print("[SERVER] Waiting for connections")

while True:
    host, addr = S.accept()
    print("[CONNECTION] Connected to:", addr)
    print("[STARTED] Game Started")
    connections += 1
    start_new_thread(threaded_client, (host, _id))
    _id += 1

# when program ends
print("[SERVER] Server offline")