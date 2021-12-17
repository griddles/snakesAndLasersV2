"""
Snakes and Lasers 2.0
A lightweight 2d arcade style game based on the classic Snake game, but with a non-osha compliant twist.

How to play:
WASD to move the snake
R to return to main menu
Speedrun mode activates a timer and automatically ends the game once you reach 200 points.
Lightweight mode removes all laser particles to reduce lag on very low end systems.
Survival mode removes the objective and decreases the time between lasers.
All three of these modes work at the same time, though Survival mode kinda defeats the purpose of Speedrun mode since
the only possible time is 3:20.000. Also, it's nearly impossible to survive for that long.

Credit:
Code - Me
Sprites - Me
Sound Effects - Me
Music - Me
Playtesting - Me, VoldmortII, and ItsTheyes
"""

import pygame as pg
import random as rnd
import tkinter as tk
import game
import network

# prepare some variables for later
tk = tk.Tk()
clock = pg.time.Clock()

# initialize pygame
pg.init()

# make it so that keypresses repeat immediately
pg.key.set_repeat(1, 1)

# render the game at 720p for consistency
screenWidth = 1280
screenHeight = 720

# find the actual resolution of the monitor so we can upscale
displayWidth = tk.winfo_screenwidth()
displayHeight = tk.winfo_screenheight()

resolutionMultiplier = displayWidth / screenWidth

# leave this at 60
framerate = 60

# set up the screen
# the base screen
baseScreen = pg.display.set_mode((displayWidth, displayHeight))
# the screen everything is drawn to, allows for screenshake
screen = pg.Surface((screenWidth, screenHeight), pg.HWACCEL)
# the offset of the drawing screen. changing it moves the entire screen
screenOffset = (0, 0)
# snakesAndLasersV2/ is required to run in VSCODE but causes errors with the .exe
# set up the two fonts used in the game
font69 = pg.font.Font(r"mojangles.otf", 69)
font32 = pg.font.Font(r"mojangles.otf", 32)

# the gameData file for high score tracking
gameData = open(r"gameData.txt", "r+")

# variables
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
lasers = []
laserChargeDuration = 2500
laserFireDuration = 1500
laserMinDelay = 6000
laserMaxDelay = 9001
laserMinDecrease = 350
laserMaxDecrease = 600
laserDelay = 6000
laserSpeed = 2
particles = []
particleLifetime = 1200
godMode = True
speedrunMode = False
surviveMode = False
multiplayerMode = True
running = True
audio = True
musicVolume = 0.75
sfxVolume = 0.75

# sprites
startButton = pg.image.load(r"sprites/start-button.png")
speedrunButtonOff = pg.image.load(r"sprites/speedrun-button-off.png")
speedrunButtonOn = pg.image.load(r"sprites/speedrun-button-on.png")
surviveButtonOff = pg.image.load(r"sprites/survive-button-off.png")
surviveButtonOn = pg.image.load(r"sprites/survive-button-on.png")
lightweightButtonOff = pg.image.load(r"sprites/lightweight-button-off.png")
lightweightButtonOn = pg.image.load(r"sprites/lightweight-button-on.png")
musicVolumeSlider = pg.image.load(r"sprites/music-volume-slider.png")
sfxVolumeSlider = pg.image.load(r"sprites/sfx-volume-slider.png")
titleImage = pg.image.load(r"sprites/title.png")

# sounds
# i use a try/except here because if a device doesnt have any audio outputs, trying to use the pygame.mixer sublibrary
# crashes the game.
try:
    selectSound = pg.mixer.Sound(r"sfx/select.wav")
    startSound = pg.mixer.Sound(r"sfx/start.wav")
    laserSound = pg.mixer.Sound(r"sfx/laserFire.wav")
    pickupSound = pg.mixer.Sound(r"sfx/pickup.wav")
    deathSound = pg.mixer.Sound(r"sfx/death.wav")

    pg.mixer.music.load(r"sfx/musicIntro.wav")
    pg.mixer.music.play()
    pg.mixer.music.queue(r"sfx/musicLoop.wav")
except: 
    audio = False

# reset the game when the player restarts it
def reset():
    global screenOffset
    global headRect
    global facing
    global segments
    global snakeTurnPos
    global objRect
    global score
    global lasers
    global laserMinDelay
    global laserMaxDelay
    global laserDelay
    global particles
    global godMode

    screenOffset = (0, 0)
    headRect = game.HeadRect(round(screenWidth / 2), round(screenHeight / 2), segments)
    facing = "W"
    segments = []
    snakeTurnPos = []
    objRect = pg.Rect((screenWidth / 3, screenHeight / 3), (15, 15))
    score = 0
    lasers = []
    laserMinDelay = 6000
    laserMaxDelay = 9001
    laserDelay = 6000
    particles = []
    godMode = True

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

# add a laser (using objects literally makes this 8 trillion times easier and less terrible)
def addLaser(startTime):
    global laserMinDelay
    global laserMaxDelay
    global laserDelay
    if multiplayerMode:
        pass
    else:
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
        decreaseDelay = rnd.randint(laserMinDecrease, laserMaxDecrease)
        if laserMinDelay > decreaseDelay + 700:
            laserMinDelay -= decreaseDelay
            laserMaxDelay -= decreaseDelay
        elif laserMaxDelay > decreaseDelay + 2000 and laserMaxDelay - decreaseDelay > laserMinDelay and surviveMode:
            laserMaxDelay -= int(round(decreaseDelay / 2))
        laserDelay = (pg.time.get_ticks() - startTime) + rnd.randint(laserMinDelay, laserMaxDelay)

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
    global laserSound
    global pickupSound
    global deathSound

    selectSound.set_volume(sfxVol)
    startSound.set_volume(sfxVol)
    laserSound.set_volume(sfxVol)
    pickupSound.set_volume(sfxVol)
    deathSound.set_volume(sfxVol)
    pg.mixer.music.set_volume(musicVol)

# the loop that handles the main menu
def menuLoop():
    global speedrunMode
    global surviveMode
    global godMode
    global particleLifetime
    global running
    global musicVolume
    global sfxVolume

    # reset the game
    reset()

    # make the mouse visible so that the user can actually click the buttons
    pg.mouse.set_visible(True)

    # has the user clicked something during this iteration of the mouse cycle?
    clicked = True

    # the loop that draws the menu
    menuRunning = True
    while menuRunning and running:
        for event in pg.event.get():
            key = pg.key.get_pressed()
            if key[pg.K_ESCAPE]:
                menuRunning = False
                running = False

        # standard button widths for visuals
        buttonWidth = startButton.get_width()
        buttonHeight = startButton.get_height()

        # the rects that handle drawing the buttons
        startRect = pg.Rect((screenWidth / 2) - (buttonWidth / 2), (screenHeight / 2) - (buttonHeight / 2), buttonWidth, buttonHeight)
        speedrunRect = pg.Rect(60, (screenHeight / 2) - (buttonHeight / 2), buttonHeight, buttonHeight)
        surviveRect = pg.Rect((screenWidth - 60) - buttonWidth, (screenHeight / 2) - (buttonHeight / 2), buttonWidth, surviveButtonOff.get_height())
        lightweightRect = pg.Rect((screenWidth / 2) - (buttonWidth / 2), (screenHeight - 60) - buttonHeight, buttonWidth, lightweightButtonOff.get_height())
        musicVolumeRect = pg.Rect(60, (screenHeight - 60 - buttonHeight), buttonWidth, buttonHeight)
        sfxVolumeRect = pg.Rect(screenWidth - 60 - buttonWidth, screenHeight - 60 - buttonHeight, buttonWidth, buttonHeight)

        titleRect = pg.Rect((screenWidth / 2) - (titleImage.get_width() / 2), 0, titleImage.get_width(), titleImage.get_height())

        # standard button widths for collision
        # (the game draws at 720p, if the resolution of the monitor is different collision gets screwed up, this fixes that)
        collideButtonWidth = buttonWidth * resolutionMultiplier
        collideButtonHeight = buttonHeight * resolutionMultiplier

        # the rects that handle collision
        collideStartRect = pg.Rect((displayWidth / 2) - (collideButtonWidth / 2), (displayHeight / 2) - (collideButtonHeight / 2), collideButtonWidth, collideButtonHeight)
        collideSpeedrunRect = pg.Rect((60 * resolutionMultiplier), (displayHeight / 2) - (collideButtonHeight / 2), collideButtonWidth, collideButtonHeight)
        collideSurviveRect = pg.Rect((displayWidth - (60 * resolutionMultiplier)) - collideButtonWidth, (displayHeight / 2) - (collideButtonHeight / 2), collideButtonWidth, collideButtonHeight)
        collideLightweightRect = pg.Rect((displayWidth / 2) - (collideButtonWidth / 2), (displayHeight - (60 * resolutionMultiplier)) - collideButtonHeight, collideButtonWidth, collideButtonHeight)
        collideMusicVolumeRect = pg.Rect(68 * resolutionMultiplier, (displayHeight - (60 * resolutionMultiplier) - collideButtonHeight), collideButtonWidth, collideButtonHeight)
        collideSfxVolumeRect = pg.Rect(displayWidth - (68 * resolutionMultiplier) - collideButtonWidth, (displayHeight - (60 * resolutionMultiplier) - collideButtonHeight), collideButtonWidth, collideButtonHeight)

        # get the x and y positions of the mouse
        mx, my = pg.mouse.get_pos()

        # if the left mouse button is down and hasn't already interacted with something
        if pg.mouse.get_pressed() == (1, 0, 0) and not clicked:
            # check collisions with all the buttons
            if collideStartRect.collidepoint(mx, my):
                menuRunning = False
                if audio:
                    pg.mixer.Sound.play(startSound)
            if collideSpeedrunRect.collidepoint(mx, my):
                speedrunMode = not speedrunMode
                clicked = True
                if audio:
                    pg.mixer.Sound.play(selectSound)
            if collideSurviveRect.collidepoint(mx, my):
                surviveMode = not surviveMode
                clicked = True
                if audio:
                    pg.mixer.Sound.play(selectSound)
            if collideLightweightRect.collidepoint(mx, my):
                particleLifetime = 1 if particleLifetime == 1200 else 1200
                clicked = True
                if audio:
                    pg.mixer.Sound.play(selectSound)

        # math for the volume sliders
        if collideMusicVolumeRect.collidepoint(mx, my) and pg.mouse.get_pressed() == (1, 0, 0) and musicVolume <= 1:
            musicVolumePosition = mx - (68 * resolutionMultiplier)
            musicVolume = ((musicVolumePosition * 100) / (collideMusicVolumeRect.width - (16 * resolutionMultiplier))) / 100
            if musicVolume > 1:
                musicVolume = 1
        if collideSfxVolumeRect.collidepoint(mx, my) and pg.mouse.get_pressed() == (1, 0, 0) and sfxVolume <= 1:
            sfxVolumePosition = mx - (displayWidth - (52 * resolutionMultiplier) - collideSfxVolumeRect.width)
            sfxVolume = ((sfxVolumePosition * 100) / (collideSfxVolumeRect.width - (16 * resolutionMultiplier))) / 100
            if sfxVolume > 1:
                sfxVolume = 1

        if audio:
            setVolume(musicVolume, sfxVolume)

        # if no mouse buttons are pressed, reset the clicked variable
        if pg.mouse.get_pressed() == (0, 0, 0):
            clicked = False

        # loop the background music
        if audio:
            if not pg.mixer.music.get_busy():
                pg.mixer.music.play()

        # draw the buttons and title image
        screen.fill((15, 15, 15))
        screen.blit(startButton, startRect)
        if speedrunMode:
            screen.blit(speedrunButtonOn, speedrunRect)
        else:
            screen.blit(speedrunButtonOff, speedrunRect)
        if surviveMode:
            screen.blit(surviveButtonOn, surviveRect)
        else:
            screen.blit(surviveButtonOff, surviveRect)
        if particleLifetime == 1:
            screen.blit(lightweightButtonOn, lightweightRect)
        else:
            screen.blit(lightweightButtonOff, lightweightRect)
        screen.blit(musicVolumeSlider, musicVolumeRect)
        screen.blit(sfxVolumeSlider, sfxVolumeRect)
        # draw the actual bar of the volume slider with the width being volume% of the maximum width
        pg.draw.rect(screen, (255, 255, 255), (musicVolumeRect.x + 8, musicVolumeRect.y + 56, (musicVolumeRect.width - 16) * musicVolume, musicVolumeRect.height - 112))
        pg.draw.rect(screen, (255, 255, 255), ((sfxVolumeRect.x + 8, sfxVolumeRect.y + 56, (sfxVolumeRect.width - 16) * sfxVolume, sfxVolumeRect.height - 112)))
        screen.blit(titleImage, titleRect)

        # send the screen to the display and update the frame
        baseScreen.blit(pg.transform.scale(screen, (displayWidth, displayHeight)), screenOffset)
        pg.display.update()
        clock.tick(framerate)

# the loop that handles running the game
def mainLoop():
    global screenOffset
    global headRect
    global facing
    global segments
    global snakeTurnPos
    global objRect
    global score
    global lasers
    global laserMinDelay
    global laserMaxDelay
    global laserMinDecrease
    global laserMaxDecrease
    global particles
    global running

    # get the mouse out of the way
    pg.mouse.set_visible(False)

    # move the objective offscreen and decrease the laser delay if we're in survival mode
    if surviveMode:
        objRect.x = -50
        objRect.y = -50
        laserMinDelay = 5000
        laserMaxDelay = 8000
        laserMinDecrease = 400
        laserMaxDecrease = 800

    if multiplayerMode:
        net = network.Network()
        headRect = net.getPlayer()
        segments = []
        for i in range(3):
            segment = game.Segment(headRect.rect.x + (segmentGap * (i + 1)), headRect.rect.y, "W")
            segments.append(segment)
            headRect.segments = segments

    # get the starting time of the game
    startTime = pg.time.get_ticks()

    score = 0

    # the actual loop
    mainRunning = True
    while mainRunning:
        if not running:
            break
        
        # handle multiplayer server updating
        if multiplayerMode:
            netSync = net.send([headRect, lasers])
            p2HeadRect = netSync[0]
            lasers = netSync[1]
            # if netSync[1] != "NONE":
            #     lasers.append(netSync[1])

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

        # remove the stored turn positions so we dont have a memory leak
        for position in snakeTurnPos:
            position.ticks += 1
            if position.ticks > (6 * (len(segments) + 1)):
                snakeTurnPos.remove(position)

        # handle picking up the objective
        if headRect.rect.colliderect(objRect):
            moveObj()
            if audio:
                pg.mixer.Sound.play(pickupSound)

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
            # if the head can collide with the first segment the snake can't turn, so ignore those collisions
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

        # if the delay is up, add a new laser
        if pg.time.get_ticks() - startTime > laserDelay and not multiplayerMode:
            addLaser(startTime)
            if audio:
                pg.mixer.Sound.play(laserSound)
        
        # increment the score every second
        if (pg.time.get_ticks() - startTime) % 1000 <= 15:
            score += 1
        
        # if we're in speedrun mode, kill the program once the score is at or above 200
        if score >= 200 and speedrunMode:
            mainRunning = False

        # get the time with the function defined earlier
        time = getTime(pg.time.get_ticks() - startTime)

        # loop the background music
        if audio:
            if not pg.mixer.music.get_busy():
                pg.mixer.music.play()

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
        
        # draw the second snake in multiplayer mode
        if multiplayerMode:
            pg.draw.rect(screen, (0, 0, 0), (p2HeadRect.rect.x - shadowDistance, p2HeadRect.rect.y + shadowDistance, p2HeadRect.rect.width, p2HeadRect.rect.height))
            pg.draw.rect(screen, (255, 0, 0), p2HeadRect)
            for segment in p2HeadRect.segments:
                pg.draw.rect(screen, (0, 0, 0), (segment.rect.x - shadowDistance, segment.rect.y + shadowDistance, segment.rect.width, segment.rect.height))
                pg.draw.rect(screen, (255, 0, 0), segment.rect)

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

        # draw all the lasers and handle the moving ones
        for laser in lasers:
            # if the laser is still charging, use a smaller width and a darker red color
            if pg.time.get_ticks() < laser.time + laserChargeDuration:
                laser.width += 0.1
                # if the laser is moving, use a bright red color
                laserColor = (175, 0, 0) if laser.moveDirection == "" else (255, 0, 0)
                if laser.direction == "H":
                    pg.draw.rect(screen, laserColor, (0, laser.pos, screenWidth, laser.width))
                elif laser.direction == "V":
                    pg.draw.rect(screen, laserColor, (laser.pos, 0, laser.width, screenHeight))
            # if the laser has finished charging, use the full width and a bright red color
            elif pg.time.get_ticks() < laser.time + laserChargeDuration + laserFireDuration:
                laser.width = 25
                # shake the screen
                screenOffset = (rnd.randint(-3, 3), rnd.randint(-3, 3))
                # move the laser and handle the rect for collision
                if laser.direction == "H":
                    laser.rect.height = laser.width
                    if laser.moveDirection == "+":
                        laser.rect.y += laserSpeed
                        tempPos = laser.rect.y
                    elif laser.moveDirection == "-":
                        laser.rect.y -= laserSpeed
                        tempPos = laser.rect.y
                    else:
                        tempPos = laser.rect.y + rnd.randint(-4, 4)
                    # draw the laser and add particles
                    pg.draw.rect(screen, (255, 0, 0), (0, tempPos, screenWidth, laser.width))
                    particles.append(game.Particle(rnd.randint(0, screenWidth), laser.rect.y + (laser.width / 2), 0, rnd.randint(-1, 1), pg.time.get_ticks()))
                    particles.append(game.Particle(rnd.randint(0, screenWidth), laser.rect.y + (laser.width / 2), 0, rnd.randint(-1, 1), pg.time.get_ticks()))
                # same but for vertical lasers
                elif laser.direction == "V":
                    laser.rect.width = laser.width
                    if laser.moveDirection == "+":
                        laser.rect.x += laserSpeed
                        tempPos = laser.rect.x
                    elif laser.moveDirection == "-":
                        laser.rect.x -= laserSpeed
                        tempPos = laser.rect.x
                    else:
                        tempPos = laser.rect.x + rnd.randint(-4, 4)
                    pg.draw.rect(screen, (255, 0, 0), (tempPos, 0, laser.width, screenHeight))
                    particles.append(game.Particle(laser.rect.x + (laser.width / 2), rnd.randint(0, screenHeight), rnd.randint(-1, 1), 0, pg.time.get_ticks()))
                    particles.append(game.Particle(laser.rect.x + (laser.width / 2), rnd.randint(0, screenHeight), rnd.randint(-1, 1), 0, pg.time.get_ticks()))
                # handle collision with the snake
                if headRect.rect.colliderect(laser.rect) and not godMode:
                    mainRunning = False
                for segment in segments:
                    if segment.rect.colliderect(laser.rect) and not godMode:
                        mainRunning = False
            # remove lasers that are done firing
            else:
                lasers.remove(laser)
                screenOffset = (0, 0)
        # draw the particles and move them
        for particle in particles:
            particle.x += particle.xSpeed
            particle.y += particle.ySpeed
            particle.xSpeed -= particle.xSpeed / 40
            particle.ySpeed -= particle.ySpeed / 40
            pg.draw.rect(screen, (255, 0, 0), (particle.x, particle.y, 5, 5))
            if pg.time.get_ticks() > particle.time + particleLifetime:
                particles.remove(particle)

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

        # loop the background music
        if audio:
            if not pg.mixer.music.get_busy():
                pg.mixer.music.play()

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
    menuLoop() 
    mainLoop() 
    endLoop() 

gameData.close() 
pg.quit() 