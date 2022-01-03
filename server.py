"""
Snakes and Lasers v2.1.1 Multiplayer Server
This allows you to host a dedicated server for Snakes and Lasers multiplayer use.
Put your local ip (win+R, cmd, ipconfig, IPv4 address) in the serverIP.txt file.
Make sure your router is port forwarding from port 6969 to your local ip.
"""

import socket
from _thread import *
import pickle
import random as rnd
import pygame as pg
import game

# initialize pygame, just because I dont understand any other timer
pg.init()

# open the ipAddress.txt file and read it
ip = open(r"serverIP.txt", "r")
ip.seek(0)
server = ip.read()

# set the port we're using
port = 6969

# set up the network socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# configure the network socket to use the ip and port we set earlier
try:
    s.bind((server, port))
except socket.error as e:
    str(e)

# allow 2 clients to connect
s.listen(2)
print("Server online, waiting for client connections...")

# initialize the players and the objective
players = [game.HeadRect(427, 240, []), game.HeadRect(853, 480, [])]
obj = game.Objective(200, 200)
score = 0

# the thread that handles the client
def threaded_client(conn, player):
    global currentPlayer
    global score

    # send the client the player object corresponding to their client number
    conn.send(pickle.dumps(players[player]))
    reply = ""
    while True:
        try:
            # recieve data from the client
            data = pickle.loads(conn.recv(2048))
            
            # update the current player object
            players[player] = data[0]
            hitObj = data[1]

            # if we didn't get any data, terminate the client connection
            if not data:
                print("Lost connection")
                break
            # otherwise, start sending data back
            else:
                reply = []
                # send back the other client's player object to be drawn on this client's screen
                if player == 1:
                    reply.append(players[0])
                else:
                    reply.append(players[1])
                # update the objective if a player hit it
                if hitObj:
                    score += 10
                    obj.x = rnd.randint(15, 1250)
                    obj.y = rnd.randint(15, 690)
                # send the client the new objective object and the current score
                reply.append(obj)
                reply.append(score)
                # send the client the current server time, for syncing
                reply.append(pg.time.get_ticks())
                # send the client a new laser, if one was created. keep this at the end, it's easier that way
                if newLaser != None:
                    reply.append(newLaser)
                    newLaser == None
                print("Recieved \"{}\"".format(data))
                print("Sending \"{}\"".format(reply))
            # actually send the data
            conn.sendall(pickle.dumps(reply))
        except:
            break
    # reset the player object being used by the client once they disconnect
    print("Client disconnected")
    players[player] = game.HeadRect(427, 240, []) if player == 0 else game.HeadRect(853, 480, [])
    currentPlayer -= 1
    conn.close()

currentPlayer = 0

lasers = []
newLaser = None

# the thread that handles laser creation (threads are cool)
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
        # only create lasers if a player is connected
        if pg.time.get_ticks() > laserDelay and currentPlayer != 0:
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

# start creating lasers
start_new_thread(threaded_lasers, ())

# start new threads for each client that connects
while True:
    conn, addr = s.accept()
    print("Connected to {}".format(addr))

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
