# Snakes and Lasers 2.1.1
A lightweight 2d arcade style game based on the classic Snake game, but with a non-osha compliant twist.

---

### Multiplayer branch:
This branch is for writing and testing an online multiplayer gamemode for Snakes and Lasers. It'll probably break the game for a while, so I'm keeping it all contained on this branch. This is very much a work in progress, so don't actually download this.

Multiplayer is currently in beta testing. This means that it's working, but still has a lot of problems, primarily with lag. It can also only be played on a local network, however this should change soon.

To-Do:
 - Add an IP address config file that will change the IP that the game tries to connect to, so players using the (nonexistent) .exe can connect to different servers
 - Fix the large amount of lag caused on anything other than a modern gaming pc
 - Make the moving lasers actually work instead of just getting really thicc (or maybe pretend that that's intended)
 - Make particles work? If they cause too much lag I'll just leave lightweight mode built in

---

### How to play:   
 - WASD to move the snake   
 - R to return to main menu   
 - Speedrun mode activates a timer and automatically ends the game once you reach 200 points.   
 - Lightweight mode removes all laser particles to reduce lag on very low end systems (like the laptop I used to make this game).   
 - Survival mode removes the objective and decreases the time between lasers.   
 - All three of these modes work at the same time, though Survival mode kinda defeats the purpose of Speedrun mode since the only possible time is 3:20.000. Also, it's nearly impossible to survive for that long.   
 - Multiplayer mode connects you to the server at the ip address in the code. If there isn't one running at that IP, it crashes. The mode allows you and one other player to share the screen, collecting the same objective, sharing a score, and dodging the same lasers. Lightweight mode is built in, since particles are completely broken, but the other two modes are untested and probably don't work.

---

### Credit:   
**Code** - Me   
**Sprites** - Me   
**Sound Effects** - Me   
**Music** - Me   
**Playtesting** - Me, VoldmortII, and ItsTheyes   
