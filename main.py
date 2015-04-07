# play order:
#  1. Choose an action to play or bluff
#  2. Announce to everyone the play
#  3. Allow other players to challenge move
#  4. If challenge succeeds, kill the player's one card
#  4.a. Check if player is dead
#  5. If challenge fails, kill challenger's one card
#  5.a. Check if player is dead
#  6. Play card's effect if no challenge or challenge fails

class Action:
    name = "Income"
    description = "Gain 1 gold"
    
    def __init__(self):
        pass
        
    def play(self, player, target = None):
        # should be overrriden by child classes
        pass
