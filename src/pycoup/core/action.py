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

from src.pycoup.core import errors
from src.pycoup.core.game import game_state

FORCE_COUP_COINS = 10


class Action:
    name: str = ""
    description: str = ""
    blocks: list[str] = []
    has_target: bool = False
    coins_needed: int = 0

    def play(self, player, target=None):
        """
        Should be overridden by child classes.
        Returns (status, response) where:
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

    def play(self, player, target=None):
        player.coins += 1
        return True, "Success"


class ForeignAid(Action):
    name = "Foreign Aid"
    description = "Gain 2 gold"

    def play(self, player, target=None):
        player.coins += 2
        return True, "Success"


class Coup(Action):
    name = "Coup"
    description = "Pay 7 gold to remove target player's influence"
    has_target = True
    coins_needed = 7

    def play(self, player, target=None):
        if player.coins < self.coins_needed:
            raise errors.NotEnoughCoinsError(self.coins_needed)

        # target should be alive
        if target is None:
            raise errors.TargetRequiredError

        if not target.alive:
            raise errors.InvalidTargetError("Target is dead")

        player.coins -= 7
        target.lose_influence()
        return True, "Success"


class Duke(Action):
    name = "Duke"
    description = "Gain 3 gold. Blocks Foreign Aid."
    blocks = ["Foreign Aid"]

    def play(self, player, target=None):
        player.coins += 3
        return True, "Success"


class Captain(Action):
    name = "Captain"
    description = "Steal 2 gold from target. Blocks Steal."
    blocks = ["Captain"]
    has_target = True

    def play(self, player, target=None):
        if target is None:
            raise errors.TargetRequiredError

        steal = min(2, target.coins)

        target.coins -= steal
        if target.coins < 0:
            target.coins = 0
        player.coins += steal

        return True, "Success"


class Contessa(Action):
    name = "Contessa"
    description = "Blocks Assasination."
    blocks = ["Assassin"]

    def play(self, player, target=None):
        raise errors.BlockOnlyError


class Assassin(Action):
    name = "Assassin"
    description = "Assasinate. Pay 3 coins to kill a player's influence."
    blocks = []
    has_target = True
    coins_needed = 3

    def play(self, player, target=None):
        if player.coins < self.coins_needed:
            raise errors.NotEnoughCoinsError(self.coins_needed)
        if target is None:
            raise errors.TargetRequiredError

        player.coins -= 3
        target.lose_influence()

        return True, "Success"


class Ambassador(Action):
    name = "Ambassador"
    description = (
        "Exchange your influence with 2 cards from the Court Deck. Blocks Steal."
    )
    blocks = ["Captain"]

    def play(self, player, target=None):
        influence_remaining = len(player.influence)
        choices = list(player.influence)

        deck_cards = [game_state.draw_card(), game_state.draw_card()]
        choices.extend(deck_cards)

        new_influence = player.select_ambassador_influence(
            list(choices), influence_remaining
        )
        if not isinstance(new_influence, list):
            new_influence = [new_influence]

        def return_cards():
            for card in deck_cards:
                game_state.add_to_deck(card)

        if len(new_influence) != influence_remaining:
            return_cards()
            raise errors.InvalidTargetError("Wrong number of cards given")

        for card in new_influence:
            if card not in choices:
                return_cards()
                raise errors.InvalidTargetError("Card given not part of valid choices")

        # give the player their new cards
        player.influence = list(new_influence)

        # return the unselected cards back to the Court Deck.
        remaining_choices = list(choices)
        for card in new_influence:
            remaining_choices.remove(card)

        for card in remaining_choices:
            game_state.add_to_deck(card)

        return True, "Success"
