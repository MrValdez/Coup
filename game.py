class GameState:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.PlayerList = []

    def requestBlocks(self, action):
        """ 
        Ask each player if they want to block. 
        If someone wants to block, return the player. Else, return None
        """
        for player in self.PlayerList:
            if player.confirmBlock(action): return player
        return None
        
GameState = GameState()     # global variable
