import action
from player import Player
from game   import GameState

import random
import os

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
    deck = [card.name for card in GameState.Deck]
    deck.sort()
    for card in deck:
        print(" ", card)

def MainLoop():
    # Infinite loop until one player remains
    global PlayersAlive, CurrentPlayer
    
    while len(PlayersAlive) > 1:
        def PrintInfo():
            os.system("cls")
            player = Players[CurrentPlayer]
            print("%s's turn" % player.name)
            print ("=================\n ")
            PrintDeckList()
            print("\nCards in hand of %s: " % (player.name), end = "")
            print (" and ".join([card.name for card in player.influence]))
            print()
        
        def PrintActions():
            print("Available actions:")
            i = 1
            for action in GameState.CommonActions:
                print (" %i: %s" % (i, action.name))
                i += 1
            for action in GameState.CardsAvailable:
                print (" %i: %s" % (i, action.name))
                i += 1
        
        def Cleanup():
            global CurrentPlayer
            CurrentPlayer += 1
            if CurrentPlayer >= len(Players): CurrentPlayer = 0
            PlayersAlive = [player for player in Players if player.alive]
            
        PrintInfo()
        PrintActions()
        input ("Action > ")
        Cleanup()
        
    print("\nThe winner is %s" % (PlayersAlive[0].name))

os.system("cls")
Setup()
PrintTurnOrder()
input("\nPress enter key to start...")
MainLoop()