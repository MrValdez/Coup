from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src.pycoup.core.errors import MajorError

if TYPE_CHECKING:
    from . import action
    from .player import Player


class CoupGame:
    def reset(self):
        self.player_list: list[Player] = []

        from . import action

        self.common_actions = [action.Income, action.ForeignAid, action.Coup]
        self.cards_available = [
            action.Duke,
            action.Captain,
            action.Assassin,
            action.Ambassador,
            action.Contessa,
        ]
        self.deck = self.cards_available * 3
        random.shuffle(self.deck)

        self.revealed_cards: list[type[action.Action]] = []

        # separating these function allow outside modules (like the unit test) to change the behavior of
        # shuffling and selecting a card
        self.random_shuffle = random.shuffle
        self.random_selector = random.choice

    def request_blocks(
        self,
        active_player: Player,
        action: type[action.Action],
        target_player: Player | None,
    ) -> tuple[Player | None, type[action.Action] | None]:
        """
        Ask each player if they want to block active player's action.
        Requests are performed in a clockwise rotation (http://boardgamegeek.com/article/18425206#18425206). However,
        for the sake of game flow, the targetted player (if any) will be requested first.
        If someone wants to block, return the tuple (player, action). Else, return (None, None).
        """
        active_index = self.player_list.index(active_player)
        player_list = self.player_list[active_index:] + self.player_list[0:active_index]

        if target_player is not None:
            target_index = self.player_list.index(target_player)
            player_list.remove(target_player)
            player_list = [self.player_list[target_index]] + player_list

        for player in player_list:
            if player == active_player or not player.alive:
                continue

            blocking_action = player.confirm_block(active_player, action)

            if blocking_action is not None:
                # check that the block is valid
                if action.name not in blocking_action.blocks:
                    continue

                return player, blocking_action

        return None, None

    def request_call_for_bluffs(
        self,
        active_player: Player,
        action: type[action.Action],
        target_player: Player | None,
    ) -> Player | None:
        """
        Ask each player if they want to call active player's (possible) bluff.
        Requests are performed in a clockwise rotation (http://boardgamegeek.com/article/18425206#18425206). However,
        for the sake of game flow, the targeted player (if any) will be requested first.
        If someone wants to call, return the player. Else, return None
        """
        active_index = self.player_list.index(active_player)
        player_list = self.player_list[active_index:] + self.player_list[0:active_index]

        if target_player is not None:
            target_index = self.player_list.index(target_player)
            player_list.remove(target_player)
            player_list = [self.player_list[target_index]] + player_list

        for player in player_list:
            if player == active_player or not player.alive:
                continue
            if player.confirm_call(active_player, action):
                return player
        return None

    def add_to_deck(self, card: type[action.Action]):
        # todo: add error handling
        self.deck.append(card)
        self.random_shuffle(self.deck)

    def draw_card(self) -> type[action.Action]:
        if not self.deck:
            raise MajorError("There is no card in the court deck!")

        card = self.random_selector(self.deck)
        self.deck.remove(card)
        return card

    def get_blocking_actions(
        self, action: type[action.Action]
    ) -> list[type[action.Action]]:
        """
        Returns all the cards that block an action.
        """
        return [card for card in self.cards_available if action.name in card.blocks]


game_state = CoupGame()  # global variable
