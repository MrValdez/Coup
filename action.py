# Actions available:
#   Income
#   ForeignAid

class Action:
    name = ""
    description = ""
    
    def __init__(self):
        pass
        
    def play(self, player, target = None):
        # should be overrriden by child classes
        pass

class Income(Action):
    name = "Income"
    description = "Gain 1 gold"
    
    def play(self, player, target = None):
        player.coins += 1
        
class ForeignAid(Action):
    name = "Foreign Aid"
    description = "Gain 2 gold"
    
    def play(self, player, target = None):
        player.coins += 2
        
class Coup(Action):
    name = "Coup"
    description = "Pay 7 gold to remove target player's influence"
    
    def play(self, player, target = None):
        # player should have 7 coins. 
        if player.coins < 7:
            return False, "Not enough coins"
            
        # target should be alive
        if target == None or not target.alive:
            return False, "Invalid target"
            
        player.coins -= 1
        target.loseInfluence()
        return True, "Success"
