import action
from player import Player
from game   import GameState

import random

# How many people are playing?
# Generate the player list
# Shuffle the player list
# Infinite loop until one player remains

PlayerCount = int(input("How many players? "))
#PlayerCount = 2

Players = []
def CreatePlayer(Number):
    player = Player()
    
    print("Player #%i" % (Number))
    player.name = input(" What is your name? ")
    #player.name = random.choice(["A", "B", "C"]) + str(Number)
    
    return player

for i in range(PlayerCount):
    Players.append(CreatePlayer(i))
    
random.shuffle(Players)

PlayersAlive = [player for player in Players if player.alive]
CurrentPlayer = 0

print ("Turn order:")
for i, player in enumerate(Players):
    print(" %i: %s" % (i + 1, player.name))

while len(PlayersAlive) > 1:
    print("Action for %s: " % (Players[CurrentPlayer].name))
    
    CurrentPlayer += 1
    if CurrentPlayer >= len(Players): CurrentPlayer = 0
    PlayersAlive = [player for player in Players if player.alive]
    input()