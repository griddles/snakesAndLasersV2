import socket
from _thread import *
import pickle
import random as rnd
import pygame as pg
import game

pg.init()

server = "192.168.208.45"
port = 6969

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Server online, waiting for client connections...")

players = [game.HeadRect(427, 240, []), game.HeadRect(853, 480, [])]
obj = game.Objective(200, 200)
score = 0

def threaded_client(conn, player):
    global currentPlayer
    global score
    conn.send(pickle.dumps(players[player]))
    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048 * 4))
            players[player] = data[0]
            hitObj = data[1]

            if not data:
                print("Lost connection")
                break
            else:
                reply = []
                if player == 1:
                    reply.append(players[0])
                else:
                    reply.append(players[1])
                if hitObj:
                    score += 10
                    obj.x = rnd.randint(15, 1250)
                    obj.y = rnd.randint(15, 690)
                reply.append(obj)
                reply.append(score)
                if newLaser != None:
                    reply.append(newLaser)
                    newLaser == None
                reply.append(pg.time.get_ticks())
                print("Recieved \"{}\"".format(data))
                print("Sending \"{}\"".format(reply))
            conn.sendall(pickle.dumps(reply))
        except:
            break
    print("Client disconnected")
    players[player] = game.HeadRect(427, 240, []) if player == 0 else game.HeadRect(853, 480, [])
    currentPlayer -= 1
    conn.close()

currentPlayer = 0

lasers = []
newLaser = None

def threaded_lasers():
    global newLaser
    global lasers
    screenWidth = 1280
    screenHeight = 720
    laserMinDelay = 6900
    laserMaxDelay = 11000
    laserDelay = 8000
    lasers = []

    while True:
        if pg.time.get_ticks() > laserDelay and currentPlayer != 0:
            startTime = pg.time.get_ticks
            # pick a random direction for the laser to fire in
            direction = rnd.choice(["H", "V"])
            moveDirection = ""
            # set the position between 0 and the applicable screen dimension
            pos = rnd.randint(0, screenHeight) if direction == "H" else rnd.randint(0, screenWidth)
            # a 50/50 chance that the laser will be moving
            if rnd.randint(0, 1) == 1:
                # always move the laser towards the center of the screen (unless it's a cross)
                if direction == "H":
                    moveDirection = "+" if pos < screenHeight / 2 else "-"
                elif direction == "V":
                    moveDirection = "+" if pos < screenWidth / 2 else "-"
            # add the laser to the list of lasers so it doesnt just disappear
            lasers.append(game.Laser(direction, pos, pg.time.get_ticks(), moveDirection))
            # a 1/3 chance that the laser will be a cross
            if rnd.randint(0, 2) == 2:
                # if it is, add another laser in the opposite direction
                if direction == "H":
                    lasers.append(game.Laser("V", rnd.randint(0, screenWidth), pg.time.get_ticks(), moveDirection))
                else:
                    lasers.append(game.Laser("H", rnd.randint(0, screenHeight), pg.time.get_ticks(), moveDirection))
            # decrease the delay between lasers by a random value, only if the current min delay is bigger than the possible max reduction
            laserDelay = pg.time.get_ticks() + rnd.randint(laserMinDelay, laserMaxDelay)
            newLaser = lasers[-1]

start_new_thread(threaded_lasers, ())

while True:
    conn, addr = s.accept()
    print("Connected to {}".format(addr))

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
