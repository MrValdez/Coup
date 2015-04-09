import random

import action

class GameState:
#    def __init__(self):
#        self.reset()
        
    def reset(self):
        self.PlayerList = []
        
        self.CommonActions = [action.Income, action.ForeignAid, action.Coup]
        self.CardsAvailable = [action.Duke, action.Captain, action.Contessa, action.Assassin, action.Ambassador]
        self.Deck = self.CardsAvailable * 3
        random.shuffle(self.Deck)
        
        self.RevealedCards = []

    def requestBlocks(self, activePlayer, action):
        """ 
        Ask each player if they want to block active player's action.
        If someone wants to block, return the tuple (player, action). Else, return (None, None)
        """
        for player in self.PlayerList:
            if player == activePlayer or not player.alive: 
                continue
            
            blockingAction = player.confirmBlock(action)
            
            if blockingAction != None: 
                # check that the block is valid
                if not action.name in blockingAction.blocks:
                    continue       
            
                return player, blockingAction
            
        return None, None

    def requestCallForBluffs(self, activePlayer, action):
        """ 
        Ask each player if they want to call active player's (possible) bluff.
        If someone wants to call, return the player. Else, return None
        """
        for player in self.PlayerList:
            if player == activePlayer or not player.alive: 
                continue
            if player.confirmCall(activePlayer, action): 
                return player
        return None

    def AddToDeck(self, card):
        # todo: add error handling
        self.Deck.append(card)
        random.shuffle(self.Deck)
    
    def DrawCard(self):
        if not len(self.Deck): return False
        
        card = random.choice(self.Deck)
        self.Deck.remove(card)
        return card

GameState = GameState()     # global variable
