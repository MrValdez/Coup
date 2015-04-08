from action import Action
from game import GameState
import random

class Player():
    def __init__(self):
        self.coins = 2
        self.alive = True
        self.influence = [Action, Action]
        
        GameState.PlayerList.append(self)
        
    def play(self, action, target = None):
        """
        1. Check if a player wants to block
        2. Check if active player wants to call bluff from blocking player  (todo: official rules says any play can call bluff. implement later)
        3. Check if any player wants to call bluff from active player
        4. Play action if successful
        """
        
        # Step 1
        blockingPlayer = GameState.requestBlocks(action)
        if blockingPlayer != None:
           # Step 2
           message = "Blocked by %s" % blockingPlayer
           return False, message
        # Step 3
        # Step 4
        status, response = action.play(action, self, target)
        
        return status, response
    
    def loseInfluence(self):
        loses = random.choice(self.influence)  # todo: change from random choice to player choice
    
        self.influence.remove(loses)
        if not len(self.influence):
            self.alive = False            
            
    def confirmBlock(self, action):
        """ returns True if player blocks action. return False if player allows action. """
        return False