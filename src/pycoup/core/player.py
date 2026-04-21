from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src.pycoup.core.action import (
    Coup,
    FORCE_COUP_COINS,
)
from src.pycoup.core import errors
from src.pycoup.core.game import game_state

if TYPE_CHECKING:
    from src.pycoup.core.action import Action


class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.name = "Noname"

        self.coins = 2
        self.alive = True

        card1 = game_state.draw_card()
        card2 = game_state.draw_card()
        self.influence = [card1, card2]
        # self.influence = [Action, Action]  # for testing purposes

        game_state.player_list.append(self)

    def give_cards(
        self, card1: type[Action], card2: type[Action] | None = None
    ) -> bool:
        """
        Give the player one or two cards.
        - If player cannot receive cards, return False.
        - If card2 is supplied but player only has one influence left, card2 will be ignored.

        Returns True on success, returns False on failure.

        todo: raise error (or return message) if card2 is supplied but player
        only have one influence left.
        """
        if not self.alive:
            return False

        influences_left = len(self.influence)
        if influences_left <= 0 or influences_left > 2:
            return False

        self.influence[0] = card1

        if len(self.influence) == 2 and card2 is not None:
            self.influence[1] = card2

        return True

    def play(
        self, action: type[Action], target: Player | None = None
    ) -> tuple[bool, str | None]:
        """
        1. Check if player is alive. If not, throw exception.
        2. Check if player has at least 12 coins. If they do, throw exception unless coup is played.
        3. Check if any player wants to call bluff from active player
           a. If someone wants to call bluff, do Call step
        4. Check if a player wants to block
           a. If active player wants to call bluff, do Call step
            todo: official rules says any play can call bluff. implement later
        5. Play action if successful
        Call step: If someone call the bluff, reveal card.
                   If card is the action played, remove influence from player.
                   Else, remove influence from calling player
        """
        if not self.alive or (target is not None and not target.alive):
            raise errors.DeadPlayerError

        if target == self:
            raise errors.TargetRequiredError

        if self.coins < action.coins_needed:
            raise errors.NotEnoughCoinsError(action.coins_needed)

        if self.coins >= FORCE_COUP_COINS and action != Coup:
            raise errors.ActionNotAllowedError(
                f"Player has {self.coins} coins. Forced Coup is the only allowed action"
            )

        # Step 3
        calling_player = None

        if (
            action in game_state.cards_available
        ):  # should only call bluff for cards, not common actions
            calling_player = game_state.request_call_for_bluffs(self, action, target)

        if calling_player is not None:
            # step 4.a
            if action in self.influence:
                # active player is telling the truth. Return the card back to the deck.
                index = self.influence.index(action)
                card = self.influence[index]
                self.influence.remove(card)
                game_state.add_to_deck(card)
                card = game_state.draw_card()
                self.influence.append(card)

                calling_player.lose_influence()
            else:
                self.lose_influence()
                message = f"Bluffing {action.name} failed for {self.name}"
                return False, message

        # Step 4
        blocking_player = None

        # should only call bluff for cards, not common actions
        if len(game_state.get_blocking_actions(action)):
            blocking_player, blocking_action = game_state.request_blocks(
                self, action, target
            )

        if blocking_player is not None and blocking_action is not None:
            # Step 3.a
            if self.confirm_call(blocking_player, blocking_action):
                if blocking_action in blocking_player.influence:
                    self.lose_influence()
                    message = f"Player {blocking_player.name} has {blocking_action.name}. Player {self.name} loses influence."
                    blocking_player.change_card(blocking_action)
                    return False, message
                else:
                    blocking_player.lose_influence()
            else:
                message = f"Blocked by {blocking_player.name}"
                return False, message

        # Step 5
        # The codebase uses classes as actions and calls them on the class itself with the class as first argument.
        status, response = action.play(action, self, target)  # type: ignore[arg-type]
        return status, response

    def lose_influence(self):
        loses = self.select_influence_to_die()

        self.influence.remove(loses)
        if len(self.influence) == 0:
            self.alive = False

        game_state.revealed_cards.append(loses)

    def confirm_call(self, active_player, action):
        """Return True if player confirms call for bluff on active player's action. Returns False if player allows action."""
        # todo: raise notImplemented. should be overriden
        return False

    def confirm_block(self, active_player, opponent_action):
        """Returns action used by player to blocks action. Return None if player allows action."""
        # todo: raise notImplemented. should be overriden
        return None

    def select_influence_to_die(self):
        """select an influence to die. returns the value from the influence list."""
        # todo: raise notImplemented. should be overriden by the input class
        # todo: change from random choice to player choice
        return random.choice(self.influence)

    def select_ambassador_influence(self, choices, influence_remaining):
        """Returns one or two cards from the choices."""
        selected = []
        for _ in range(influence_remaining):
            card = random.choice(choices)
            selected.append(card)
            choices.remove(card)

        return selected

    def change_card(self, card):
        """
        Change card to a new card from the player deck. This is called when a card is exposed after a call for bluff.
        """
        if card not in self.influence:
            # todo: create a Coup-specific exception
            raise BaseException(
                f"{card} is not found in player's influence. Something went wrong"
            )

        self.influence.remove(card)
        game_state.add_to_deck(card)

        new_card = game_state.draw_card()
        self.influence.append(new_card)
