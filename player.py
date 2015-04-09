from action import Action, Coup, DeadPlayer, ActionNotAllowed, TargetRequired, NotEnoughCoins
from game import GameState
import random

class Player():
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.name = "Noname"
        
        self.coins = 2
        self.alive = True
        
        card1 = GameState.DrawCard()
        card2 = GameState.DrawCard()
        self.influence = [card1, card2]
        #self.influence = [Action, Action]  # for testing purposes
        
        GameState.PlayerList.append(self)
        
    def giveCards(self, card1, card2 = None):
        """
        Give the player one or two cards. 
         If player cannot receive cards, return False.
         If card2 is supplied but player only has one influence left, card2 will be ignored.
         Returns True on success, returns False on failure. Todo: raise error (or return message) if card2 is supplied but player
         only have one influence left.
        """
        if not self.alive:
            return False
            
        influencesLeft = len(self.influence)
        if influencesLeft <= 0 or influencesLeft > 2: 
            return False
        
        self.influence[0] = card1
        
        if len(self.influence) == 2:
            self.influence[1] = card2
            
        return True
        
    def play(self, action, target = None):
        """
        1. Check if player is alive. If not, throw exception.
        2. Check if player has at least 12 coins. If they do, throw exception unless coup is played.
        3. Check if a player wants to block
           a. If active player wants to call bluff, do Call step (todo: official rules says any play can call bluff. implement later)
        4. Check if any player wants to call bluff from active player
           a. If someone wants to call bluff, do Call step
        5. Play action if successful
        Call step: If someone call the bluff, reveal card. 
                   If card is the action played, remove influence from player.
                   Else, remove influence from calling player        
        """        
        if not self.alive or (target != None and not target.alive):
            raise DeadPlayer
            
        if target == self:
            raise TargetRequired
            
        if self.coins < action.coinsNeeded:
            raise NotEnoughCoins(action.coinsNeeded)
        
        if self.coins >= 12 and action != Coup:
            raise ActionNotAllowed("Player has %i coins. Forced Coup is the only action" % (self.coins))
        
        # Step 3
        blockingPlayer = None
        
        # should only call bluff for cards, not common actions
        # iterate each available cards and check if move can be blocked
        for card in GameState.CardsAvailable:
            if action.name in card.blocks:
                blockingPlayer, blockingAction = GameState.requestBlocks(self, action)
                break
        
        if blockingPlayer != None:
            # Step 3.a
            if self.confirmCall(blockingPlayer, blockingAction):
                if blockingAction in blockingPlayer.influence:
                    self.loseInfluence()
                    message = "Player %s has %s. Player %s loses influence." % (blockingPlayer.name, blockingAction.name, self.name)
                    blockingPlayer.changeCard(blockingAction)
                    return False, message
                else:
                    blockingPlayer.loseInfluence()
            else:
                message = "Blocked by %s" % blockingPlayer.name
                return False, message
        
        # Step 4
        
        callingPlayer = None
        if action in GameState.CardsAvailable:      # should only call bluff for cards, not common actions
            callingPlayer = GameState.requestCallForBluffs(self, action)
            
        if callingPlayer != None:
            # step 4.a
            if action in self.influence:
                callingPlayer.loseInfluence()
            else:
                self.loseInfluence()
                message = "Bluffing %s failed for %s" % (action.name, self.name)
                return False, message             
        
        # Step 5
        status, response = action.play(action, self, target)
        return status, response
    
    def loseInfluence(self):
        loses = self.selectInfluenceToDie()
    
        self.influence.remove(loses)
        if len(self.influence) == 0:
            self.alive = False            
        
        GameState.RevealedCards.append(loses)
            
    def confirmCall(self, activePlayer, action): 
        """ return True if player confirms call for bluff on active player's action. returns False if player allows action. """
        # todo: raise notImplemented. should be overriden
        return False
            
    def confirmBlock(self, opponentAction):
        """ returns action used by player to blocks action. return None if player allows action. """
        # todo: raise notImplemented. should be overriden
        return None
        
    def selectInfluenceToDie(self):
        """ select an influence to die. returns the value from the influence list. """
        # todo: raise notImplemented. should be overriden by the input class
        return random.choice(self.influence)  # todo: change from random choice to player choice
        
    def selectAmbassadorInfluence(self, choices, influenceRemaining):
        """ returns one or two cards from the choices. """
        # todo: raise notImplemented. should be overriden by the input class
        
        selected = []
        for i in range(influenceRemaining):
            card = random.choice(choices)
            selected.append(card)
            choices.remove(card)
            
        return selected
        
    def changeCard(self, card):
        """
        change card to a new card from the player deck. This is called when a card is exposed after a call for bluff.
        """
        if not card in self.influence:
            # todo: create a Coup-specific exception
            raise BaseException("%s is not found in player's influence. Something went wrong" % card)
            
        self.influence.remove(card)
        GameState.AddToDeck(card)
        
        newCard = GameState.DrawCard()
        self.influence.append(newCard)
