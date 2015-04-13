# Actions implemented:
#   Income
#   Foreign Aid
#   Coup
#   Duke
#   Captain
#   Contessa
#   Assassin
#   Ambassador

# Hardcoded value
#   ForceCoupCoins

from core.errors import *
from core.game import GameState

ForceCoupCoins = 10

class Action:
    name = ""
    description = ""
    blocks = []
    hasTarget = False
    coinsNeeded = 0
            
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
    hasTarget = True
    coinsNeeded = 7
    
    def play(self, player, target = None):
        if player.coins < self.coinsNeeded:
            raise NotEnoughCoins(self.coinsNeeded)
            
        # target should be alive
        if target == None:
            raise TargetRequired
                        
        if not target.alive:
            raise InvalidTarget("Target is dead")
            
        player.coins -= 7
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
    hasTarget = True
            
    def play(self, player, target = None):
        if target == None:
            raise TargetRequired
    
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
        raise BlockOnly
        
class Assassin(Action):
    name = "Assassin"
    description = "Assasinate. Pay 3 coins to kill a player's influence."
    blocks = []
    hasTarget = True
    coinsNeeded = 3
    
    def play(self, player, target = None):
        if player.coins < self.coinsNeeded:
            raise NotEnoughCoins(self.coinsNeeded)
        if target == None:
            raise TargetRequired
            
        player.coins -= 3
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
            
        if len(newInfluence) != influenceRemaining:
            # There is a missing card. Try again.
            ReturnCards()
            raise InvalidTarget("Wrong number of cards given")

        choicesCopy = list(choices) # this allow us to test for card duplicates
        for card in newInfluence:
            if not card in choicesCopy:
                # something is wrong. The player sent a card choice that is not part of the original choices.
                # try again.
                ReturnCards()
                raise InvalidTarget("Card given not part of valid choices")
            
            choicesCopy.remove(card)
        
        # give the player their new cards        
        player.influence = list(newInfluence)

        # return the unselected cards back to the Court Deck.
        for card in newInfluence:
            choices.remove(card)
            
        for card in choices:
            GameState.AddToDeck(card)
        return True, "Success"
