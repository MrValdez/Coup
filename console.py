import action
from player import Player
from game   import GameState

import random
import os

# Freemode allows the game to allow for any cards to be played
FreeMode = True
FreeMode = False

defaultNames = ["Leonardo", "Michelangelo", "Raphael", "Donatello", "Splinter", "April"]

Players = []
PlayersAlive = []
CurrentPlayer = 0

AvailableActions = []

class ConsolePlayer(Player):
    ShowBlockOptions = True         # global variable to show possible options for blocking. set to True every turn

    def confirmCall(self, activePlayer, action): 
        """ return True if player confirms call for bluff on active player's action. returns False if player allows action. """
        choice = input ("%s, do you think %s's %s is a bluff?\n Do you want to call (Y/N)? " % (self.name, activePlayer.name, action.name))
        choice = choice.upper()
        
        if not choice.strip() in ('Y', 'N', ''):
            print (" Type Y to call bluff. Type N or press enter to allow %s's %s." % (activePlayer.name, action.name))
            return self.confirmCall(activePlayer, action)
            
        if choice == 'Y':
            return True
               
        return False 
            
    def confirmBlock(self, activePlayer, opponentAction):
        """ returns action used by player to blocks action. return None if player allows action. """
        cardBlockers = []
        
        for card in GameState.CardsAvailable:
            if opponentAction.name in card.blocks:
                cardBlockers.append(card)

        totalBlockers = len(cardBlockers) + 1
        
        if ConsolePlayer.ShowBlockOptions:
            ConsolePlayer.ShowBlockOptions = False
            
            print ("\n%s's %s can be blocked with the following cards:" % (activePlayer.name, opponentAction.name))
            for i, card in enumerate(cardBlockers):
                print(" %i: %s" % (i + 1, card.name))
            print(" %i: (Do not block)\n" % (totalBlockers))            
            
        choice = input("%s, do you wish to block %s (1-%i)? " % (self.name, opponentAction.name, totalBlockers))
        choice = choice.strip()
        if choice == "":
            choice = str(totalBlockers)      # do not block
        
        if not choice.isnumeric():
            print (" Select a number between 1-%i. Press enter to allow %s's %s." % (totalBlockers, activePlayer.name, opponentAction.name))
            return self.confirmBlock(opponentAction)
        choice = int(choice) - 1
        
        if choice == len(cardBlockers):
            return None         # player decides not to block
        
        if not (choice >= 0 and choice < len(cardBlockers)):
            print (" Select a number between 1-%i. Press enter to allow %s's %s." % (totalBlockers, activePlayer.name, opponentAction.name))
            return self.confirmBlock(opponentAction)
            
        block = cardBlockers[choice - 1]
        
        print("\n\n%s is blocking with %s" % (self.name, block.name))
        return block
        
    def selectInfluenceToDie(self):
        """ select an influence to die. returns the value from the influence list. """
        # todo: raise notImplemented. should be overriden by the input class
        print ("\n%s has lost an influence!" % (self.name))
        
        if len(self.influence) == 1:
            print ("%s will lose their last card, %s" % (self.name, self.influence[0].name))
            return self.influence[0]
        
        print ("%s, select influence to lose:" % (self.name))
        for i, card in enumerate(self.influence):
            print (" %i: %s" % (i + 1, card.name))
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
        
        def askChoice(choices, inputMessage):
            for i, choice in enumerate(choices):
                print (" %i: %s" % (i + 1, choice.name))
            card = input (inputMessage)
            
            if not card.isnumeric():
                return askChoice(choices, inputMessage)
                
            card = int(card) - 1
            if card < 0 or card >= len(choices):
                return askChoice(choices, inputMessage)
            
            card = choices[card]
            return card
        
        print("\n%s, these are the cards you drew:" % (self.name))
        
        card1 = askChoice(choices, "Select the first card to take>")
        choices.remove(card1)
        
        if (influenceRemaining == 1):
            return [card1]
        else:
            print("")
            card2 = askChoice(choices, "Select the second card to take>")
            return [card1, card2]

def ClearScreen():
    # todo: make this crossplatform
    os.system("cls")
    
def PrintTurnOrder():
    ClearScreen()
    print ("Turn order:")
    for i, player in enumerate(Players):
        print(" %i: %s" % (i + 1, player.name))

def PrintDeckList():
    print ("There are %i cards in the Court Deck" % (len(GameState.Deck)))
    
    if FreeMode:
        # calculate what cards can be in the court deck
        deck = GameState.CardsAvailable * 3
        for player in Players:
            for card in player.influence:
                try:
                    deck.remove(card)
                except ValueError:
                    # one of the players received more than 3 copies of a card.
                    # add a "fake card" into the deck as indicator
                    class FakeCard(action.Action):  pass
                    FakeCard.name = "%s (Extra)" % (card.name)
                    deck.append(FakeCard)
        for card in GameState.RevealedCards:
            deck.remove(card)
            
        deck = [card.name for card in deck]
        deck.sort()
        
        print("Theoritical cards are:")
        for card in deck:
            print(" ", card)

def PrintRevealedCards():
    size = len(GameState.RevealedCards)
    if size == 0:
        return
        
    print ("There are %i cards that has been revealed:" % (size))

    reveals = [card.name for card in GameState.RevealedCards]
    reveals.sort()
    for card in reveals:
        print(" ", card)

def PrintActions():
    for i, action in enumerate(AvailableActions):
        if action.name != "Contessa":   # ignore Contessa as a possible action.
            print (" %i: %s" % (i + 1, action.name))
    print (" X: Exit the game")

def SelectCards(message, twoCards):
    print(message)
    for i, card in enumerate(GameState.CardsAvailable):
        print("%i: %s" % (i + 1, card.name))
    
    def InputCard(message):
        card = input(message)
        if not card.isnumeric():
            return InputCard(message)
        card = int(card) - 1
        
        if not (card >= 0 and card < len(GameState.CardsAvailable)):
            return InputCard(message)
            
        return GameState.CardsAvailable[card]
    
    card1 = InputCard("Card #1: ")
    
    if not twoCards:
        return [card1]
    else:
        card2 = InputCard("Card #2: ")
        return [card1, card2]
        
def SetupActions():
    global AvailableActions
    for action in GameState.CommonActions:
        AvailableActions.append(action)
    for action in GameState.CardsAvailable:
        AvailableActions.append(action)

def SetupRNG():
    """ This setups the RNG to have the cards come from the user instead """
    if not FreeMode:
        return
    
    def randomShuffle(deck):    pass            # does not shuffle
    def randomSelector(deck):    
        message = "Select the card the player received: "
        cards = SelectCards(message, False)
        return cards[0]
    
    GameState.randomShuffle  = randomShuffle
    GameState.randomSelector = randomSelector
    

def Setup():
    # How many people are playing?
    # Generate the player list
    # Shuffle the player list
    GameState.reset()
    SetupActions()
    
    def GetNumberOfPlayers():
        PlayerCount = input("How many players (2-6)? ")
        if not PlayerCount.isnumeric():
            return GetNumberOfPlayers()
        
        PlayerCount = int(PlayerCount)
        if PlayerCount < 2 or PlayerCount > 6:
            return GetNumberOfPlayers()
            
        return PlayerCount
        
    PlayerCount = GetNumberOfPlayers()
    #PlayerCount = 2        # for testing purposes
    
    def CreatePlayer(Number):
        player = ConsolePlayer()
        
        player.name = input("Player #%i: What is your name (Leave blank for a random name)? " % (Number + 1))
                
        if player.name.strip() == "":
            player.name = random.choice(defaultNames)
            defaultNames.remove(player.name)
            print(" Player %i's name is %s\n" % (Number + 1, player.name))
            
        if FreeMode:                
            message = "Select %s's cards" % (player.name)
            player.influence = SelectCards(message, True)
            
            print(" Player %s is holding: %s and %s\n" % (player.name, player.influence[0].name, player.influence[1].name))
                
        return player

    print("\n")
    for i in range(PlayerCount):
        Players.append(CreatePlayer(i))
        
    SetupRNG()
    random.shuffle(Players)

    global PlayersAlive
    PlayersAlive = [player for player in Players if player.alive]
    
def MainLoop():
    # Infinite loop until one player remains
    global PlayersAlive, CurrentPlayer, GameIsRunning
    
    GameIsRunning = True
    while GameIsRunning and len(PlayersAlive) > 1:
        player = Players[CurrentPlayer]
        ConsolePlayer.ShowBlockOptions = True
        
        def PrintInfo():
            os.system("cls")
            
            PlayerList = Players[CurrentPlayer:] + Players[0:CurrentPlayer]
            paddingWidth = 16
            
            for playerInfo in PlayerList:            
                name = playerInfo.name 
                if len(name) > paddingWidth - 4: 
                    name = name[:paddingWidth - 4] + "... "
                
                padding = " " * (paddingWidth - len(name))
                print("%s" % (name), end = padding)                    

            
            print("")
            for playerInfo in PlayerList:            
                coins = playerInfo.coins
                coins = "Coins: %i" % (coins)
                coins = coins.rjust(2)
                
                padding = " " * (paddingWidth - len(coins))
                print(coins, end = padding)
            
            print("\n(Active player)")
            print("" + "=" * (paddingWidth * len(PlayerList))  + "\n")
            PrintDeckList()
            PrintRevealedCards()
            print("\n%s's cards are: " % (player.name))
            heldCards = " and ".join([card.name for card in player.influence])
            print(" " + heldCards + "\n")
        
        def Cleanup():
            global CurrentPlayer
            CurrentPlayer += 1
            if CurrentPlayer >= len(Players): CurrentPlayer = 0
            
            global PlayersAlive 
            PlayersAlive = [player for player in Players if player.alive]
        
        def ChooseAction():    
            move = input ("Action> ")
            if not move.isnumeric():
                if move.upper() == "X":
                    confirm = input ("\nAre you sure you want to exit (Y/N)? ")
                    if confirm.upper() != "Y":                      
                        ChooseAction()
                        return  
                    
                    global GameIsRunning    
                    GameIsRunning = False
                    return
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
                
                PossibleTargets = [player for player in PossibleTargets if player.alive]
                
                if len(PossibleTargets) == 1:
                    return PossibleTargets[0]
                
                print()
                for i, iterPlayer in enumerate(PossibleTargets):
                    print(" %i: %s" % (i + 1, iterPlayer.name))
                target = input ("Choose a target>")
                
                if not target.isnumeric():
                    return ChooseTarget()
                target = int(target) - 1
                if target < 0 or target >= len(PossibleTargets):
                    return ChooseTarget()
                
                return PossibleTargets[target]

            if player.coins >= action.ForceCoupCoins and AvailableActions[move].name != "Coup":
                print("Player has %i coins. Forced Coup is the only allowed action" % (player.coins))
                ChooseAction()
                return            
            
            target = None
            if AvailableActions[move].hasTarget:
                target = ChooseTarget()

            try:
                ClearScreen()
                print("%s is playing %s" % (player.name, AvailableActions[move].name), end = '')
                if not target is None:
                    print(" (target: %s)" % (target.name))
                
                print("")
                
                status, response = player.play(AvailableActions[move], target)
            except action.ActionNotAllowed as e:
                print(e.message)
                ChooseAction()
                return
            except action.NotEnoughCoins as exc:
                print(" You need %i coins to play %s. You only have %i coins." % (exc.coinsNeeded, AvailableActions[move].name, player.coins))
                ChooseAction()
                return
            except action.BlockOnly:
                print("You cannot play %s as an action" % (AvailableActions[move].name))
                ChooseAction()
                return
            except action.TargetRequired:                        
                target = ChooseTarget()
                status, response = player.play(AvailableActions[move], target)
                
            if status == False:
                print (response)
            
        if player.alive:
            PrintInfo()
            print("\nAvailable actions:")
            PrintActions()
            ChooseAction()
            
            if GameIsRunning: input("\nPress enter key to continue...")
        Cleanup()
        
    print("\nThe winner is %s" % (PlayersAlive[0].name))

def main():
    ClearScreen()
    Setup()
    PrintTurnOrder()
    input("\nPress enter key to start...")
    MainLoop()
    
if __name__ == "__main__":
    main()