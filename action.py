# Actions available:
#   Income
#   Foreign Aid
#   Coup
#   Duke
#   Captain
#   Contessa
#   Assassin
#   Ambassador

# to be implemented:
#   Forced Coup

from game import GameState

class Action:
    name = ""
    description = ""
    blocks = []
            
    def play(self, player, target = None):
        """
         should be overrriden by child classes
         returns (status, response) where 
           status:     True/False if action is successful or not
           response:   String explaining status. Usually reserved for explanation of why an action failed.
         Example:
            return True, "Success"
            return False, "Failed because it was blocked"
        """
        return False, None
        
class Income(Action):
    name = "Income"
    description = "Gain 1 gold"
    
    def play(self, player, target = None):
        player.coins += 1
        return True, "Success"
        
class ForeignAid(Action):
    name = "Foreign Aid"
    description = "Gain 2 gold"
    
    def play(self, player, target = None):
        player.coins += 2
        return True, "Success"
        
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

class Duke(Action):
    name = "Duke"
    description = "Gain 3 gold. Blocks Foreign Aid."
    blocks = ["Foreign Aid"]
            
    def play(self, player, target = None):
        player.coins += 3
        return True, "Success"
        
class Captain(Action):
    name = "Captain"
    description = "Steal 2 gold from target. Blocks Steal."
    blocks = ["Captain"]
            
    def play(self, player, target = None):
        if target == None:
            raise BaseException     #todo: make Coup-specific exception on missing target
    
        steal = 0
        if target.coins >= 2:
            steal = 2
        elif target.coins == 1:
            steal = 1
            
        target.coins -= steal
        if target.coins < 0: target.coins = 0
        player.coins += steal
        
        return True, "Success"
        
class Contessa(Action):
    name = "Contessa"
    description = "Blocks Assasination."
    blocks = ["Assassin"]
            
    def play(self, player, target = None):
        raise BaseException     #todo: make Coup-specific exception on Contessa un-usable as an action
        
class Assassin(Action):
    name = "Assassin"
    description = "Assasinate. Pay 2 coins to kill a player's influence."
    blocks = []
            
    def play(self, player, target = None):
        if target == None:
            raise BaseException     #todo: make Coup-specific exception on missing target
            
        target.loseInfluence()
        
        return True, "Success"
        
class Ambassador(Action):
    name = "Ambassador"
    description = "Exchange your influence with 2 cards from the Court Deck. Blocks Steal."
    blocks = ["Captain"]
            
    def play(self, player, target = None):
        influenceRemaining = len(player.influence)
        choices = list(player.influence)
        
        deckCards = [GameState.DrawCard(), GameState.DrawCard()]
        choices.append(deckCards[0])
        choices.append(deckCards[1])
        
        newInfluence = player.selectAmbassadorInfluence(list(choices), influenceRemaining)
        if type(newInfluence) != list:
            newInfluence = [newInfluence]
        
        def ReturnCards():
            GameState.AddToDeck(deckCards[0])
            GameState.AddToDeck(deckCards[1])
            raise BaseException     #todo: make Coup-specific exception to select new cards for Ambassador
            
        if len(newInfluence) != influenceRemaining:
            # There is a missing card. Try again.
            ReturnCards()
        
        for card in newInfluence:
            if not card in choices:
                # something is wrong. The player sent a card choice that is not part of the original choices.
                # try again.
                ReturnCards()
        
        # give the player their new cards        
        player.influence = list(newInfluence)

        # return the unselected cards back to the Court Deck.
        for card in newInfluence:
            choices.remove(card)
               
        for card in choices:
            GameState.AddToDeck(card)
        
        return True, "Success"
