#todo: blocks
#      bluffs

import action
from player import Player
from game   import GameState

import random
import os

class ConsolePlayer(Player):
    def confirmCall(self, activePlayer, action): 
        """ return True if player confirms call for bluff on active player's action. returns False if player allows action. """
        choice = input ("%s: Do you think %s's %s is a bluff? Do you want to call (Y/N)? " % (self.name, activePlayer.name, action.name))
        choice = choice.upper()
        
        if not choice in ('Y', 'N'):
            print (" Type Y or N.")
            return self.confirmCall(activePlayer, action)
            
        if choice == 'Y':
            return True
        
        return False
            
    def confirmBlock(self, opponentAction):
        """ returns action used by player to blocks action. return None if player allows action. """
        cardBlockers = []
        
        for card in GameState.CardsAvailable:
            if opponentAction.name in card.blocks:
                cardBlockers.append(card)

        print ("%s can be blocked with the following cards:" % (opponentAction.name))
        for i, card in enumerate(cardBlockers):
            print("%i: %s" % (i + 1, card.name))
        print("%i: (Do not block)" % (len(cardBlockers) + 1))
            
        choice = input(" Which card should %s use to block? " % (self.name))
        if not choice.isnumeric():
            print ("Invalid choice, try again\n")
            return self.confirmBlock(opponentAction)
        choice = int(choice) - 1
        
        if choice == len(cardBlockers):
            return None         # player decides not to block
        
        if not (choice >= 0 and choice < len(cardBlockers)):
            print ("Invalid choice, try again\n")
            return self.confirmBlock(opponentAction)
            
        block = cardBlockers[choice - 1]
        
        print("%s is blocking with %s" % (self.name, block.name))
        return block
        
    def selectInfluenceToDie(self):
        """ select an influence to die. returns the value from the influence list. """
        # todo: raise notImplemented. should be overriden by the input class
        print ("%s has lost the challenge. " % (self.name))
        
        if len(self.influence) == 1:
            print ("%s will lose their last card, %s" % (self.name, self.influence[0].name))
            return self.influence[0]
        
        print ("Select influence to lose:")
        for i, card in enumerate(self.influence):
            print ("%i: %s" % (i + 1, card))
        choice = input("> ")
        if not choice.isnumeric():
            print ("Invalid choice, try again\n")
            return self.selectInfluenceToDie()
        choice = int(choice)
        if not (choice == 1 or choice == 2):
            print ("Invalid choice, try again\n")
            return self.selectInfluenceToDie()
        if choice > len(self.influence):
            print ("Invalid choice, try again\n")
            return self.selectInfluenceToDie()
            
        return self.influence[choice - 1]

    def selectAmbassadorInfluence(self, choices, influenceRemaining):
        """ returns one or two cards from the choices. """
        finalChoices = []
        
        def askChoice(choices):
            for i, choice in enumerate(choices):
                print ("%i: %s" % (i + 1, choice.name))
            card = input ("Select a card> ")
            
            if not card.isnumeric():
                return askChoice(choices)
                
            card = int(card) - 1
            if card < 0 or card >= len(choices):
                return askChoice(choices)
            
            card = choices[card]
            print ("Selected %s" % (card.name))
            return card
            
        card1 = askChoice(choices)
        choices.remove(card1)
        
        if (influenceRemaining == 1):
            return [card1]
        else:
            card2 = askChoice(choices)
            return [card1, card2]
        
Players = []
PlayersAlive = []
CurrentPlayer = 0

AvailableActions = []
def SetupActions():
    global AvailableActions
    for action in GameState.CommonActions:
        AvailableActions.append(action)
    for action in GameState.CardsAvailable:
        AvailableActions.append(action)

def Setup():
    # How many people are playing?
    # Generate the player list
    # Shuffle the player list

    GameState.reset()
    #PlayerCount = int(input("How many players? "))
    PlayerCount = 2

    def CreatePlayer(Number):
        player = ConsolePlayer()
        
        print("Creating Player #%i" % (Number + 1))
        #player.name = input(" What is your name? ")
        player.name = random.choice(["A", "B", "C"]) + str(Number)
        
        player.loseInfluence()
        
        return player

    for i in range(PlayerCount):
        Players.append(CreatePlayer(i))
        
    random.shuffle(Players)

    global PlayersAlive
    PlayersAlive = [player for player in Players if player.alive]
    
    SetupActions()

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
        player = Players[CurrentPlayer]
        
        def PrintInfo():
            os.system("cls")
            print("%s's turn" % player.name)
            print(" Coins: %i" % player.coins)
            print("=================\n ")
            PrintDeckList()
            print("\nCards in hand of %s: " % (player.name), end = "")
            print(" and ".join([card.name for card in player.influence]))
            print()

        def PrintActions():
            print("Available actions:")
            for i, action in enumerate(AvailableActions):
                print (" %i: %s" % (i + 1, action.name))
        
        def Cleanup():
            global CurrentPlayer
            CurrentPlayer += 1
            if CurrentPlayer >= len(Players): CurrentPlayer = 0
            
            global PlayersAlive 
            PlayersAlive = [player for player in Players if player.alive]
        
        def ChooseAction():    
            move = input ("Action> ")
            if not move.isnumeric():
                ChooseAction()
                return
            move = int(move) - 1
            
            if not (move >= 0 and move < len(AvailableActions)):
                ChooseAction()
                return
            
            status = False
            
            def ChooseTarget():
                PossibleTargets = list(Players)
                PossibleTargets.remove(player)          #todo: remove this to test if the program handles targetting self
                
                #todo: add code to remove dead players from list.
                
                if len(PossibleTargets) == 1:
                    return PossibleTargets[0]
                
                for i, iterPlayer in enumerate(PossibleTargets):
                    print(" %i: %s" % (i + 1, iterPlayer.name))
                target = input ("Choose a target>")
                
                if not target.isnumeric():
                    return ChooseTarget()
                target = int(target) - 1
                if target < 0 or target >= len(PossibleTargets):
                    return ChooseTarget()
                
                return PossibleTargets[target]

            target = None
            if AvailableActions[move].hasTarget:
                target = ChooseTarget()
            
            print("%s is playing %s" % (player.name, AvailableActions[move].name), end = '')
            if not target is None:
                print(" (target: %s)" % (target.name))
            else:
                print("")

            try:
                status, response = player.play(AvailableActions[move], target)
            except action.ActionNotAllowed as e:
                print(e.message)
                ChooseAction()
            except action.BlockOnly:
                print("You cannot play %s as an action" % (AvailableActions[move].name))
                ChooseAction()
            except action.TargetRequired:                        
                target = ChooseTarget()
                status, response = player.play(AvailableActions[move], target)
                
            if status == False:
                print (response)
            
        if player.alive:
            PrintInfo()
            PrintActions()
            ChooseAction()
        Cleanup()
        input("\nPress enter key to continue...")
        
    print("\nThe winner is %s" % (PlayersAlive[0].name))

os.system("cls")
Setup()
PrintTurnOrder()
input("\nPress enter key to start...")
MainLoop()