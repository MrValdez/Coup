class GameState:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.PlayerList = []

    def requestBlocks(self, activePlayer, action):
        """ 
        Ask each player if they want to block active player's action.
        If someone wants to block, return the player. Else, return None
        """
        for player in self.PlayerList:
            if player == activePlayer: continue
            if player.confirmBlock(action): return player
        return None

    def requestCallForBluffs(self, activePlayer, action):
        """ 
        Ask each player if they want to call active player's (possible) bluff.
        If someone wants to call, return the player. Else, return None
        """
        for player in self.PlayerList:
            if player == activePlayer: continue
            if player.confirmCall(action): return player
        return None
        
GameState = GameState()     # global variable