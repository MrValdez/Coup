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