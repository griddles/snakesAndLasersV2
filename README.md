# Snakes and Lasers v2.1.1
A lightweight 2d arcade style game based on the classic Snake game, but with a non-osha compliant twist.

---

### How to play:   
 - WASD to move the snake   
 - R to return to main menu   
 - Speedrun mode activates a timer and automatically ends the game once you reach 200 points. NinjaPerfect currently holds the world record, at 34.344 seconds.  
 - Lightweight mode removes all laser particles to reduce lag on very low end systems (like the laptop I used to make this game).   
 - Survival mode removes the objective and decreases the time between lasers.   
 - All three of these modes work at the same time, though Survival mode kinda defeats the purpose of Speedrun mode since the only possible time is 3:20.000. Also, it's nearly impossible to survive for that long.   
 - Multiplayer mode connects you to the server at the ip address in the code. If there isn't one running at that IP, it crashes. The mode allows you and one other player to share the screen, collecting the same objective, sharing a score, and dodging the same lasers. Lightweight mode is built in, since particles are completely broken, Survive mode does nothing, and Speedrun mode disconnects you if the score is higher than 200. If the server score is already higher, it prevents you from connecting.

I know that you can easily just edit gameData.txt to change your highscore. I really don't care, its only
there to help you know what your highscore is and when you beat it. Learning how to make permanent values that can't be changed manually isn't worth it for this purpose.

also, if for some reason you have a monitor with a smaller resolution than 720p, this game will probably cause a ton of lag because apparently downscaling is harder than upscaling. I cant fix this unless I run the game in 480p, or lower, and that would be terrible and garbage, so too bad.

---

### Credit:   
**Code** - Me   
**Sprites** - Me   
**Sound Effects** - Me   
**Music** - Me   
**Playtesting** - Me, VoldmortII, ItsTheyes, and Ninjaperfect   
