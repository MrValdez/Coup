import action
from player import Player
from game   import GameState

import random

Players = []
PlayersAlive = []
CurrentPlayer = 0

def Setup():
    # How many people are playing?
    # Generate the player list
    # Shuffle the player list

    GameState.reset()
    #PlayerCount = int(input("How many players? "))
    PlayerCount = 2

    def CreatePlayer(Number):
        player = Player()
        
        print("Creating Player #%i" % (Number + 1))
        #player.name = input(" What is your name? ")
        player.name = random.choice(["A", "B", "C"]) + str(Number)
        
        return player

    for i in range(PlayerCount):
        Players.append(CreatePlayer(i))
        
    random.shuffle(Players)

    global PlayersAlive
    PlayersAlive = [player for player in Players if player.alive]

def PrintTurnOrder():
    print ("Turn order:")
    for i, player in enumerate(Players):
        print(" %i: %s" % (i + 1, player.name))

def PrintDeckList():
    print ("Cards in Court Deck (%i cards):" % (len(GameState.Deck)))
    for card in GameState.Deck:
        print(" ", card.name)

def MainLoop():
    # Infinite loop until one player remains
    global PlayersAlive, CurrentPlayer
    
    while len(PlayersAlive) > 1:
        PrintDeckList()
        player = Players[CurrentPlayer]
        print("Action for %s: " % (player.name))
        for card in player.influence:
            print(" ", card.name, end = "")
        print("\n")
        
        CurrentPlayer += 1
        if CurrentPlayer >= len(Players): CurrentPlayer = 0
        PlayersAlive = [player for player in Players if player.alive]
        input()

Setup()
PrintTurnOrder()
MainLoop()