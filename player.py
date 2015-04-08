from action import Action
from game import GameState
import random

class Player():
    def __init__(self):
        self.name = "Noname"
        
        self.coins = 2
        self.alive = True
        self.influence = [Action, Action]
        
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
        1. Check if a player wants to block
           a. If active player wants to call bluff, do Call step (todo: official rules says any play can call bluff. implement later)
        2. Check if any player wants to call bluff from active player
           a. If active want to call bluff, do Call step
        4. Play action if successful
        Call step: If someone call the bluff, reveal card. 
                   If card is the action played, remove influence from player.
                   Else, remove influence from calling player        
        """
        
        # Step 1
        blockingPlayer, blockingAction = GameState.requestBlocks(self, action)
        
        if blockingPlayer != None:
            # Step 1.a
            if self.confirmCall(blockingPlayer, blockingAction):
                if blockingAction in blockingPlayer:
                    self.loseInfluence()
                    message = "Player %s has %s. Player %s loses influence." % (blockingPlayer.name, blockingAction.name, self.name)
                    blockingPlayer.changeCard(blockingAction)
                    return False, message
                else:
                    blockingPlayer.loseInfluence()
            else:
                message = "Blocked by %s" % blockingPlayer.name
                return False, message
        
        # Step 3
        callingPlayer = GameState.requestCallForBluffs(self, action)
        if callingPlayer != None:
            if action in self.influence:
                callingPlayer.loseInfluence()
            else:
                self.loseInfluence()
                message = "Bluffing %s failed for %s" % (action.name, self)
                return False, message             
        
        # Step 4
        status, response = action.play(action, self, target)
        return status, response
    
    def loseInfluence(self):
        loses = random.choice(self.influence)  # todo: change from random choice to player choice
    
        self.influence.remove(loses)
        if not len(self.influence):
            self.alive = False            
            
    def confirmCall(self, activePlayer, action): 
        """ return True if player confirms call for bluff on active player's action. returns False if player allows action. """
        # todo: raise notImplemented. should be overriden
        return False
            
    def confirmBlock(self, action):
        """ returns action used by player to blocks action. return None if player allows action. """
        # todo: raise notImplemented. should be overriden
        return None