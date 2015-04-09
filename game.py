import random

import action

class GameState:
    def reset(self):
        self.PlayerList = []
        
        self.CommonActions = [action.Income, action.ForeignAid, action.Coup]
        self.CardsAvailable = [action.Duke, action.Captain, action.Contessa, action.Assassin, action.Ambassador]
        self.Deck = self.CardsAvailable * 3
        random.shuffle(self.Deck)
        
        self.RevealedCards = []
        
        # separating these function allow outside modules (like the unit test) to change the behavior of
        # shuffling and selecting a card
        self.randomShuffle = random.shuffle
        self.randomSelector = random.choice

    def requestBlocks(self, activePlayer, action, targetPlayer):
        """ 
        Ask each player if they want to block active player's action.
        Requests are performed in a clockwise rotation (http://boardgamegeek.com/article/18425206#18425206). However,
        for the sake of game flow, the targetted player (if any) will be requested first.
        If someone wants to block, return the tuple (player, action). Else, return (None, None).
        """
        ActiveIndex = self.PlayerList.index(activePlayer)
        PlayerList = self.PlayerList[ActiveIndex:] + self.PlayerList[0:ActiveIndex]
        
        if targetPlayer != None:
            TargetIndex = self.PlayerList.index(targetPlayer)
            PlayerList.remove(targetPlayer)
            PlayerList = [self.PlayerList[TargetIndex]] + PlayerList
        
        for player in PlayerList:
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
        Requests are performed in a clockwise rotation (http://boardgamegeek.com/article/18425206#18425206).
        If someone wants to call, return the player. Else, return None
        """
        ActiveIndex = self.PlayerList.index(activePlayer)
        PlayerList = self.PlayerList[ActiveIndex:] + self.PlayerList[0:ActiveIndex]

        for player in PlayerList:
            if player == activePlayer or not player.alive: 
                continue
            if player.confirmCall(activePlayer, action): 
                return player
        return None

    def AddToDeck(self, card):
        # todo: add error handling
        self.Deck.append(card)
        self.randomShuffle(self.Deck)
    
    def DrawCard(self):
        if not len(self.Deck): raise action.MajorError("There is no card in the court deck!")
        
        card = self.randomSelector(self.Deck)
        self.Deck.remove(card)
        return card

    def getBlockingActions(self, action):
        """
        returns all the cards the block an action
        """
        blockers = []
        for card in GameState.CardsAvailable:
            if action.name in card.blocks:
                blockers.append(card)
                
        return blockers
            
GameState = GameState()     # global variable
