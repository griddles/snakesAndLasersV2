"""
Snakes and Lasers v2.1.1 Client
A lightweight 2d arcade style game based on the classic Snake game, but with a non-osha compliant twist.

How to play:
 - WASD to move the snake
 - R to return to main menu
 - Speedrun mode activates a timer and automatically ends the game once you reach 200 points.
 - Lightweight mode removes all laser particles and screenshake to reduce lag on very low end systems 
   (like the laptop I used to make this game).
 - Survival mode removes the objective and decreases the time between lasers.   
 - All three of these modes work at the same time, though Survival mode kinda defeats the purpose of 
   Speedrun mode since the only possible time is 3:20.000. Also, it's nearly impossible to survive for 
   that long.
 - Multiplayer mode connects you to the server at the ip address in the code. If there isn't one running 
   at that IP, it crashes. The mode allows you and one other player to share the screen, collecting the 
   same objective, sharing a score, and dodging the same lasers. Lightweight mode is built in, since 
   particles are completely broken, Survive mode does nothing, and Speedrun mode disconnects you if the 
   score is higher than 200. If the server score is already higher, it prevents you from connecting.

Credit:
Code - Me
Sprites - Me
Sound Effects - Me
Music - Me
Playtesting - Me, VoldmortII, Theyes, and NinjaPerfect
"""

import pygame as pg
import random as rnd
import tkinter as tk
import game

# initialize tkinter and the ingame clock
tk = tk.Tk()
clock = pg.time.Clock()

# initialize pygame
pg.init()

# set key repeat delay to 1 to avoid non-registered keypresses
pg.key.set_repeat(1, 1)

# render the game at 720p for consistency
screenWidth = 1280
screenHeight = 720

# find the actual resolution of the monitor so we can upscale (only works on 16:9 and similar monitors)
displayWidth = tk.winfo_screenwidth()
displayHeight = tk.winfo_screenheight()

resolutionMultiplier = displayWidth / screenWidth

# keep a framerate of 60, any other value breaks the game
framerate = 60

# set up the screen
# the base screen
baseScreen = pg.display.set_mode((displayWidth, displayHeight))
# the screen everything is drawn to, allows for screenshake
screen = pg.Surface((screenWidth, screenHeight), pg.HWACCEL)
# the offset of the drawing screen. changing it moves the entire screen
screenOffset = (0, 0)
screenShake = True

# depending on the directory of these files, you might have to add snakesandlasersv2/ in front of the path
# set up the two fonts used in the game
font69 = pg.font.Font(r"mojangles.otf", 69) # nice lol
font32 = pg.font.Font(r"mojangles.otf", 32)

# the gameData file for high score tracking
gameData = open(r"gameData.txt", "r+")

# just a few variables
segments = []
headRect = game.HeadRect(round(screenWidth / 2), round(screenHeight / 2), segments)
facing = "W"
speed = 5
segmentGap = 30
snakeSize = 25
snakeColor = (255, 255, 255)
shadowDistance = 5
snakeTurnWaitTime = 150
snakeTurnPos = []
objRect = pg.Rect((screenWidth / 3, screenHeight / 3), (15, 15))
objColor = (0, 0, 255)
objScore = 10
score = 0
highScore = gameData.read()
gameData.seek(0)
godMode = False
speedrunMode = False
surviveMode = False
lightweightMode = False
multiplayerMode = False
running = True
audio = True
musicVolume = 0.75
sfxVolume = 0.75

# load in all the sprites used
startButton = pg.image.load(r"sprites/start-button.png")
speedrunButtonOff = pg.image.load(r"sprites/speedrun-button-off.png")
speedrunButtonOn = pg.image.load(r"sprites/speedrun-button-on.png")
surviveButtonOff = pg.image.load(r"sprites/survive-button-off.png")
surviveButtonOn = pg.image.load(r"sprites/survive-button-on.png")
lightweightButtonOff = pg.image.load(r"sprites/lightweight-button-off.png")
lightweightButtonOn = pg.image.load(r"sprites/lightweight-button-on.png")
multiplayerButtonOff = pg.image.load(r"sprites/multiplayer-button-off.png")
multiplayerButtonOn = pg.image.load(r"sprites/multiplayer-button-on.png")
musicVolumeSlider = pg.image.load(r"sprites/music-volume-slider.png")
sfxVolumeSlider = pg.image.load(r"sprites/sfx-volume-slider.png")
titleImage = pg.image.load(r"sprites/title.png")

# load all the sounds
# i use a try/except here because if a device doesnt have any audio outputs, trying to use the pygame.mixer 
# sublibrary crashes the game
try:
    selectSound = pg.mixer.Sound(r"sfx/select.wav")
    startSound = pg.mixer.Sound(r"sfx/start.wav")
    pickupSound = pg.mixer.Sound(r"sfx/pickup.wav")
    deathSound = pg.mixer.Sound(r"sfx/death.wav")
except: 
    audio = False

# reset the game when the player dies or restarts
def reset():
    global screenOffset
    global headRect
    global facing
    global segments
    global snakeTurnPos
    global objRect
    global score
    global godMode

    screenOffset = (0, 0)
    headRect = game.HeadRect(round(screenWidth / 2), round(screenHeight / 2), segments)
    facing = "W"
    segments = []
    snakeTurnPos = []
    objRect = pg.Rect((screenWidth / 3, screenHeight / 3), (15, 15))
    score = 0
    godMode = False

    # add the first three segments so the snake starts out with 4 total body parts
    for i in range(3):
        segment = game.Segment(headRect.rect.x + (segmentGap * (i + 1)), headRect.rect.y, "W")
        segments.append(segment)

# move the objective and increase the score
def moveObj():
    global objRect
    global score
    objRect.x = rnd.randint(objRect.width, screenWidth - objRect.width * 2)
    objRect.y = rnd.randint(objRect.height, screenHeight - objRect.height * 2)
    score += objScore
    addSegment()

# add a new segment that's facing the same direction as the end segment
def addSegment():
    x = 0
    y = 0
    if segments[-1].direction == "N":
        y = segments[-1].rect.y + segmentGap
    elif segments[-1].direction == "S":
        y = segments[-1].rect.y - segmentGap
    elif segments[-1].direction == "W":
        x = segments[-1].rect.x + segmentGap
    elif segments[-1].direction == "E":
        x = segments[-1].rect.x - segmentGap
    if x == 0:
        x = segments[-1].rect.x
    elif y == 0:
        y = segments[-1].rect.y
    segments.append(game.Segment(x, y, segments[-1].direction))
    headRect.segments = segments

# take the current game ticks and return a string in 00:00.000 format
def getTime(ticks):
    milliseconds = ticks
    seconds = 0
    minutes = 0
    while milliseconds >= 1000:
        seconds += 1
        milliseconds -= 1000
    while seconds >= 60:
        minutes += 1
        seconds -= 60
    time = "{:0>2}:{:0>2}.{:0>3}".format(minutes, seconds, milliseconds)
    return time

# set the volume for both the music and the sound effects
def setVolume(musicVol, sfxVol):
    global selectSound
    global startSound
    global pickupSound
    global deathSound

    selectSound.set_volume(sfxVol)
    startSound.set_volume(sfxVol)
    pickupSound.set_volume(sfxVol)
    deathSound.set_volume(sfxVol)
    pg.mixer.music.set_volume(musicVol)

# the loop that handles running the game
def mainLoop():
    global screenOffset
    global headRect
    global facing
    global segments
    global snakeTurnPos
    global objRect
    global score
    global running

    reset()

    # get the mouse out of the way
    pg.mouse.set_visible(False)

    screenShake = True

    # get the starting time of the game
    startTime = pg.time.get_ticks()

    score = 0

    frame = 2

    # the main game loop
    mainRunning = True
    while mainRunning:
        if not running:
            break
            
        frame += 1

        # loop through all the keypresses stored.
        for event in pg.event.get():
            key = pg.key.get_pressed()
            if key[pg.K_ESCAPE]:
                mainRunning = False
                running = False
            # set the direction of the snake, and set the turn position.
            if (key[pg.K_w] or key[pg.K_UP]) and not facing == "S" and not facing == "N":
                facing = "N"
                snakeTurnPos.append(game.TurnPos(headRect.rect.x, headRect.rect.y, "N", 0))
            if (key[pg.K_s] or key[pg.K_DOWN]) and not facing == "N" and not facing == "S":
                facing = "S"
                snakeTurnPos.append(game.TurnPos(headRect.rect.x, headRect.rect.y, "S", 0))
            if (key[pg.K_a] or key[pg.K_LEFT]) and not facing == "E" and not facing == "W":
                facing = "W"
                snakeTurnPos.append(game.TurnPos(headRect.rect.x, headRect.rect.y, "W", 0))
            if (key[pg.K_d] or key[pg.K_RIGHT]) and not facing == "W" and not facing == "E":
                facing = "E"
                snakeTurnPos.append(game.TurnPos(headRect.rect.x, headRect.rect.y, "E", 0))
            if key[pg.K_r]:
                mainRunning = False

        # handle turning the snake segments
        for segment in segments:
            for position in snakeTurnPos:
                if (segment.rect.x, segment.rect.y) == (position.x, position.y):
                    segment.direction = position.direction

        # remove the stored turn positions so we dont break the game
        for position in snakeTurnPos:
            position.ticks += 1
            if position.ticks > (6 * (len(segments) + 1)):
                snakeTurnPos.remove(position)

        # handle picking up the objective
        if headRect.rect.colliderect(objRect):
            if multiplayerMode:
                hitObj = True
            else:
                moveObj()
            if audio:
                pg.mixer.Sound.play(pickupSound)
        else:
            hitObj = False

        # move the snake in the direction it's facing
        if facing == "N":
            headRect.rect.y -= speed
        elif facing == "S":
            headRect.rect.y += speed
        elif facing == "W":
            headRect.rect.x -= speed
        elif facing == "E":
            headRect.rect.x += speed
        
        # move the segments along with the head
        for segment in segments:
            if segment.direction == "N":
                segment.rect.y -= speed
            elif segment.direction == "S":
                segment.rect.y += speed
            elif segment.direction == "W":
                segment.rect.x -= speed
            elif segment.direction == "E":
                segment.rect.x += speed
        
        # handle collision between the head and the body segments
        for segment in segments:
            # when the snake turns the head collides with the first segment, so ignore that collision
            if segments.index(segment) == 0:
                continue
            else:
                if headRect.rect.colliderect(segment.rect) and not godMode:
                    mainRunning = False
        
        # teleport the snake to the other side when it hits an edge
        if headRect.rect.x < 0:
            headRect.rect.x = screenWidth - snakeSize
        elif headRect.rect.x > screenWidth - snakeSize:
            headRect.rect.x = 0
        if headRect.rect.y < 0:
            headRect.rect.y = screenHeight - snakeSize
        elif headRect.rect.y > screenHeight - snakeSize:
            headRect.rect.y = 0

        # same for the segments
        for segment in segments:
            if segment.rect.x < 0:
                segment.rect.x = screenWidth - snakeSize
            elif segment.rect.x > screenWidth - snakeSize:
                segment.rect.x = 0
            if segment.rect.y < 0:
                segment.rect.y = screenHeight - snakeSize
            elif segment.rect.y > screenHeight - snakeSize:
                segment.rect.y = 0
        
        # increment the score every second
        if (pg.time.get_ticks() - startTime) % 1000 <= 15 and not multiplayerMode:
            score += 1

        # get the time with the function defined earlier
        time = getTime(pg.time.get_ticks() - startTime)

        # update the segments attribute on headRect
        headRect.segments = segments

        screen.fill((15, 15, 15))
        # draw the snake
        pg.draw.rect(screen, (0, 0, 0), (headRect.rect.x - shadowDistance, headRect.rect.y + shadowDistance, headRect.rect.width, headRect.rect.height))
        if multiplayerMode:
            pg.draw.rect(screen, (0, 0, 255), headRect.rect)
        else:
            pg.draw.rect(screen, snakeColor, headRect.rect)
        for segment in segments:
            pg.draw.rect(screen, (0, 0, 0), (segment.rect.x - shadowDistance, segment.rect.y + shadowDistance, segment.rect.width, segment.rect.height))
            if multiplayerMode:
                pg.draw.rect(screen, (0, 0, 255), segment.rect)
            else:
                pg.draw.rect(screen, snakeColor, segment.rect)

        # draw the obj
        pg.draw.rect(screen, (0, 0, 0), (objRect.x - shadowDistance, objRect.y + shadowDistance, 15, 15))
        pg.draw.rect(screen, objColor, objRect)

        # draw the score
        shadowText = font69.render(str(score), False, (0, 0, 0))
        scoreText = font69.render(str(score), False, (255, 255, 255))
        screen.blit(shadowText, ((screenWidth / 2) - font69.size(str(score))[0] / 2 - shadowDistance, round(screenHeight / 20 + shadowDistance)))
        screen.blit(scoreText, ((screenWidth / 2) - font69.size(str(score))[0] / 2, round(screenHeight) / 20))

        # draw the highscore
        highScoreText = font32.render("High: " + str(highScore), False, (255, 255, 255))
        screen.blit(highScoreText, (30, 20))

        # draw the current time if we're in speedrun mode
        if speedrunMode:
            timeText = font32.render(time, False, (255, 255, 255))
            screen.blit(timeText, ((screenWidth - font32.size(time)[0]) - 15, 15))

        currentTime = pg.time.get_ticks()
    
        # send the screen to the display and update it
        baseScreen.blit(pg.transform.scale(screen, (displayWidth, displayHeight)), screenOffset)
        pg.display.update()
        clock.tick(framerate)

# the death screen loop
def endLoop():
    global running
    global highScore

    # play the death sound effect
    if audio:
        pg.mixer.Sound.play(deathSound)
    
    # save the highscore (if we got one) in the gamedata file
    if score > int(highScore):
        gameData.truncate(0)
        gameData.seek(0)
        gameData.write(str(score))
        gameData.seek(0)
        highScore = score

    # the actual loop for the death screen
    endRunning = True
    while endRunning:
        if not running:
            break
        for event in pg.event.get():
            key = pg.key.get_pressed()
            if key[pg.K_ESCAPE]:
                endRunning = False
                running = False
        
        # move on to the menu if the left mouse button is pressed
        if pg.mouse.get_pressed(num_buttons=3) == (1, 0, 0):
            endRunning = False
        
        # the game over text
        shadowGameoverText = font69.render("Game Over", False, (0, 0, 0))
        gameoverText = font69.render("Game Over", False, (255, 255, 255))
        shadowContinueText = font32.render("LMB to continue", False, (0, 0, 0))
        continueText = font32.render("LMB to continue", False, (255, 255, 255))

        # draw the game over text
        screen.blit(shadowGameoverText, ((screenWidth / 2) - font69.size("Game Over")[0] / 2 - shadowDistance, (screenHeight / 2) - font69.size("Game Over")[1] / 2 + shadowDistance))
        screen.blit(gameoverText, ((screenWidth / 2) - font69.size("Game Over")[0] / 2, (screenHeight / 2) - font69.size("Game Over")[1] / 2))
        screen.blit(shadowContinueText, ((screenWidth / 2) - font32.size("LMB to continue")[0] / 2 - shadowDistance, (screenHeight / 2) + font69.size("Game Over")[1] + (font32.size("LMB to continue")[1] / 2) + 15 + shadowDistance))
        screen.blit(continueText, ((screenWidth / 2) - font32.size("LMB to continue")[0] / 2, (screenHeight / 2) + font69.size("Game Over")[1] + (font32.size("LMB to continue")[1] / 2) + 15))

        # send the screen to the display and update the frame
        baseScreen.blit(pg.transform.scale(screen, (displayWidth, displayHeight)), screenOffset)
        pg.display.update()
        clock.tick(framerate)

# repeatedly run through each of the three loops until the user hits escape
while running: 
    mainLoop()
    endLoop()

gameData.close() 
pg.quit()

# this game has a total of 1048 lines of code across all 4 files (client.py, network.py, server.py, and game.py)