import pygame as pg
import tkinter as tk

tk = tk.Tk()
screenWidth = tk.winfo_screenwidth()
screenHeight = tk.winfo_screenheight()

class HeadRect:
    def __init__(self, x, y):
        self.rect = pg.Rect((x, y), (25, 25))

class Segment:
    def __init__(self, posX, posY, dir):
        self.direction = dir
        self.rect = pg.Rect((posX, posY), (25, 25))

class TurnPos:
    def __init__(self, xPos, yPos, dir, ticks):
        self.x = xPos
        self.y = yPos
        self.direction = dir
        self.time = ticks

class Laser:
    def __init__(self, dir, position, startTime, moveDir):
        self.direction = dir
        self.pos = position
        self.time = startTime
        self.moveDirection = moveDir
        if dir == "V":
            self.rect = pg.Rect((position, 0), (25, screenHeight))
        else:
            self.rect = pg.Rect((0, position), (screenWidth, 25))
    width = 5

class Particle:
    def __init__(self, posX, posY, speedX, speedY, ticks):
        self.x = posX
        self.y = posY
        self.xSpeed = speedX
        self.ySpeed = speedY
        self.time = ticks