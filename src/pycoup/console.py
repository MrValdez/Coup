import os
import random

from src.pycoup.core import action, errors
from src.pycoup.core.game import game_state
from src.pycoup.core.player import Player

# Freemode allows the game to allow for any cards to be played
FREE_MODE = False

DEFAULT_NAMES = [
    "Leonardo",
    "Michelangelo",
    "Raphael",
    "Donatello",
    "Splinter",
    "April",
]

players: list[Player] = []
players_alive: list[Player] = []
current_player: int = 0

available_actions: list[action.Action] = []
game_is_running: bool = False


class ConsolePlayer(Player):
    show_block_options = True

    def confirm_call(self, active_player, action):
        """Return True if player confirms call for bluff on active player's action. Returns False if player allows action."""
        if len(players_alive) > 2:
            longest_name = max(len(player.name) for player in players_alive)
            name = self.name + "," + (" " * (longest_name - len(self.name)))
        else:
            name = self.name + ","

        choice = input(
            f"{name} do you think {active_player.name}'s {action.name} is a bluff?\n Do you want to call (Y/N)? "
        )
        choice = choice.upper().strip()

        if choice not in ("Y", "N", ""):
            print(
                f"\n Type Y to call bluff. \n Type N or press enter to allow {active_player.name}'s {action.name}.\n"
            )
            return self.confirm_call(active_player, action)

        return choice == "Y"

    def confirm_block(self, active_player, opponent_action):
        """Returns action used by player to block action. Returns None if player allows action."""
        card_blockers = []

        for card in game_state.cards_available:
            if opponent_action.name in card.blocks:
                card_blockers.append(card)

        total_blockers = len(card_blockers) + 1

        if ConsolePlayer.show_block_options:
            ConsolePlayer.show_block_options = False

            print(
                f"\n{active_player.name}'s {opponent_action.name} can be blocked with the following cards:"
            )
            for i, card in enumerate(card_blockers):
                print(f" {i + 1}: {card.name}")
            print(f" {total_blockers}: (Do not block)\n")

        if len(players_alive) > 2:
            longest_name = max(len(player.name) for player in players_alive)
            name = self.name + "," + (" " * (longest_name - len(self.name)))
        else:
            name = self.name + ","

        choice = input(
            f"{name} do you wish to block {opponent_action.name} (1-{total_blockers})? "
        ).strip()
        if choice == "":
            choice = str(total_blockers)  # do not block

        if not choice.isnumeric():
            print(
                f" Select a number between 1-{total_blockers}. Press enter to allow {active_player.name}'s {opponent_action.name}."
            )
            return self.confirm_block(active_player, opponent_action)

        choice_int = int(choice) - 1

        if choice_int == len(card_blockers):
            return None  # player decides not to block

        if not (choice_int >= 0 and choice_int < len(card_blockers)):
            print(
                f" Select a number between 1-{total_blockers}. Press enter to allow {active_player.name}'s {opponent_action.name}."
            )
            return self.confirm_block(active_player, opponent_action)

        block = card_blockers[choice_int]
        print(f"\n\n{self.name} is blocking with {block.name}")
        return block

    def select_influence_to_die(self):
        """Select an influence to die. Returns the value from the influence list."""
        print(f"\n{self.name} has lost an influence!")

        if len(self.influence) == 1:
            print(f"{self.name} will lose their last card, {self.influence[0].name}")
            return self.influence[0]

        print(f"{self.name}, select influence to lose:")
        for i, card in enumerate(self.influence):
            print(f" {i + 1}: {card.name}")

        choice = input("> ")
        if choice.isnumeric():
            choice_int = int(choice)
            if choice_int in [1, 2]:
                return self.influence[choice_int - 1]

        print("Invalid choice, try again\n")
        return self.select_influence_to_die()

    def select_ambassador_influence(self, choices, influence_remaining):
        """Returns one or two cards from the choices."""

        def ask_choice(choices, input_message):
            print("")
            for i, choice in enumerate(choices):
                print(f" {i + 1}: {choice.name}")
            print("")

            card_idx = input(input_message)
            if card_idx.isnumeric():
                idx = int(card_idx) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
            return ask_choice(choices, input_message)

        clear_screen("Ambassador success", 24)
        print(f"\n{self.name}, these are the cards you drew:")

        card1 = ask_choice(choices, "Select the first card to take> ")
        choices.remove(card1)

        if influence_remaining == 1:
            return [card1]
        else:
            print("")
            card2 = ask_choice(choices, "Select the second card to take> ")
            return [card1, card2]


def clear_screen(header_message, header_size=10):
    # http://stackoverflow.com/a/2084628/1599
    os.system("cls" if os.name == "nt" else "clear")

    # http://stackoverflow.com/questions/17254780/printing-extended-ascii-characters-in-python-3-in-both-windows-and-linux
    dic = {
        "\\": b"\xe2\x95\x9a",
        "-": b"\xe2\x95\x90",
        "/": b"\xe2\x95\x9d",
        "|": b"\xe2\x95\x91",
        "+": b"\xe2\x95\x94",
        "%": b"\xe2\x95\x97",
    }

    def decode(x):
        return "".join(dic.get(i, i.encode("utf-8")).decode("utf-8") for i in x)

    print(decode(f"+{'-' * header_size}%%"))
    print(decode(f"|{header_message.center(header_size)}|"))
    print(decode(f"\\{'-' * header_size}/"))


def print_turn_order(current_player_shown):
    header = [" Turn order", ""]

    for i, player in enumerate(players):
        header_str = f"   {i + 1}: {player.name}"
        if player == current_player_shown:
            header_str = "  >" + header_str.strip()
        header.append(header_str)

    max_len = max(len(row) for row in header) + 2
    for i, row in enumerate(header):
        header[i] = row + (" " * (max_len - len(row)))

    header[1] = "-" * max_len
    clear_screen("|\n|".join(header), max_len)


def print_deck_list():
    print(f"There are {len(game_state.deck)} cards in the Court Deck")

    if FREE_MODE:
        # calculate what cards can be in the court deck
        deck = game_state.cards_available * 3
        for player in players:
            for card in player.influence:
                try:
                    deck.remove(card)
                except ValueError:
                    # one of the players received more than 3 copies of a card.
                    # add a "fake card" into the deck as indicator
                    class FakeCard(action.Action):
                        pass

                    FakeCard.name = f"{card.name} (Extra)"
                    deck.append(FakeCard)
        for card in game_state.revealed_cards:
            deck.remove(card)

        deck_names = sorted(card.name for card in deck)

        print("Theoretical cards are:")
        for card in deck_names:
            print(" ", card)


def print_revealed_cards():
    size = len(game_state.revealed_cards)
    if size == 0:
        return

    print(f"There are {size} cards that have been revealed:")

    reveals = sorted(card.name for card in game_state.revealed_cards)
    for card in reveals:
        print(f"    {card}")


def print_actions():
    for i, avail_action in enumerate(available_actions):
        if avail_action.name != "Contessa":  # ignore Contessa as a possible action.
            print(f" {i + 1}: {avail_action.name}")
    print(" X: Exit the game")


def select_cards(message, two_cards):
    print(message)
    for i, card in enumerate(game_state.cards_available):
        print(f"{i + 1}: {card.name}")

    def input_card(msg):
        card_idx = input(msg)
        if card_idx.isnumeric():
            idx = int(card_idx) - 1
            if 0 <= idx < len(game_state.cards_available):
                return game_state.cards_available[idx]
        return input_card(msg)

    card1 = input_card("Card #1: ")

    if not two_cards:
        return [card1]
    else:
        card2 = input_card("Card #2: ")
        return [card1, card2]


def setup_actions():
    global available_actions
    available_actions.extend(game_state.common_actions)
    available_actions.extend(game_state.cards_available)


def setup_rng():
    """This setups the RNG to have the cards come from the user instead"""
    if not FREE_MODE:
        return

    def random_shuffle(deck):
        pass  # does not shuffle

    def random_selector(deck):
        message = "Select the card the player received: "
        cards = select_cards(message, False)
        return cards[0]

    game_state.random_shuffle = random_shuffle
    game_state.random_selector = random_selector


def setup():
    # How many people are playing?
    # Generate the player list
    # Shuffle the player list
    game_state.reset()
    setup_actions()

    def get_number_of_players():
        player_count = input("How many players (2-6)? ")
        if player_count.isnumeric():
            player_count_int = int(player_count)
            if 2 <= player_count_int <= 6:
                return player_count_int
        print("Invalid input, please enter a number between 2 and 6.")
        return get_number_of_players()

    player_count = get_number_of_players()

    def create_player(number):
        player = ConsolePlayer()
        name = input(
            f"Player #{number + 1}: What is your name (Leave blank for a random name)? "
        ).strip()

        if name == "":
            name = random.choice(DEFAULT_NAMES)
            DEFAULT_NAMES.remove(name)
            print(f" Player {number + 1}'s name is {name}\n")
        player.name = name

        if FREE_MODE:
            message = f"Select {player.name}'s cards"
            player.influence = select_cards(message, True)
            print(
                f" Player {player.name} is holding: {player.influence[0].name} and {player.influence[1].name}\n"
            )

        return player

    print("\n")
    for i in range(player_count):
        players.append(create_player(i))

    setup_rng()
    random.shuffle(players)

    global players_alive
    players_alive = [player for player in players if player.alive]


def main_loop():
    # Infinite loop until one player remains
    global players_alive, current_player, game_is_running

    game_is_running = True
    while game_is_running and len(players_alive) > 1:
        player = players[current_player]
        ConsolePlayer.show_block_options = True

        def print_info():
            player_list = players[current_player:] + players[0:current_player]
            padding_width = 16
            header_list = []
            header_str = ""
            row_width = 0

            for player_info in player_list:
                name = player_info.name
                if len(name) > padding_width - 4:
                    name = name[: padding_width - 4] + "... "

                padding = " " * (padding_width - len(name))
                header_str += name + padding

            header_str = header_str.rstrip()
            row_width = max(row_width, len(header_str) + 4)
            header_str = "  " + header_str
            header_list.append(header_str)
            header_str = ""

            for player_info in player_list:
                coins = f"Coins: {player_info.coins}"
                coins = coins.rjust(2)

                padding = " " * (padding_width - len(coins))
                header_str += coins + padding

            header_str = "  " + header_str
            header_str = header_str.rstrip()
            row_width = max(row_width, len(header_str))
            header_list.append(header_str)

            header_str = "(Active player)" + (padding_width * " ")
            row_width = max(row_width, len(header_str))
            header_list.append(header_str)

            for i, header in enumerate(header_list):
                header_list[i] += " " * (row_width - len(header_list[i]))

            clear_screen("|\n|".join(header_list), row_width)

            print("")
            print_deck_list()
            print_revealed_cards()
            print(f"\n\n{player.name}'s cards are: ")
            held_cards = " and ".join(card.name for card in player.influence)
            print(f"    {held_cards}")

        def cleanup():
            global current_player, players_alive
            current_player += 1
            if current_player >= len(players):
                current_player = 0
            players_alive = [p for p in players if p.alive]

        def choose_action():
            global game_is_running
            move_str = input("Action> ").strip()
            if move_str.upper() == "X":
                confirm = (
                    input("\nAre you sure you want to exit (Y/N)? ").strip().upper()
                )
                if confirm == "Y":
                    game_is_running = False
                    return
                return choose_action()

            if move_str.isnumeric():
                move = int(move_str) - 1
                if not (0 <= move < len(available_actions)):
                    return choose_action()

            def choose_target():
                possible_targets = [p for p in players if p != player and p.alive]

                if len(possible_targets) == 1:
                    return possible_targets[0]

                print()
                for i, iter_player in enumerate(possible_targets):
                    print(f" {i + 1}: {iter_player.name}")

                target_idx = input("Choose a target> ").strip()
                if target_idx.isnumeric():
                    idx = int(target_idx) - 1
                    if 0 <= idx < len(possible_targets):
                        return possible_targets[idx]
                return choose_target()

            action_obj = available_actions[move]
            if player.coins < action_obj.coins_needed:
                print(
                    f" You need {action_obj.coins_needed} coins to play {action_obj.name}. You only have {player.coins} coins."
                )
                return choose_action()

            if player.coins >= action.FORCE_COUP_COINS and action_obj.name != "Coup":
                print(
                    f"Player has {player.coins} coins. Forced Coup is the only allowed action"
                )
                return choose_action()

            target = choose_target() if action_obj.has_target else None

            try:
                header = []
                header_str = f"{player.name} is playing {action_obj.name}"
                header_len = len(header_str) + 4
                header_str = header_str.center(header_len)
                header.append(header_str)

                if target is not None:
                    header_str = f" (target: {target.name})"
                    header_str += " " * (header_len - len(header_str))
                    header.append(header_str)

                clear_screen("|\n|".join(header), header_len)
                print("")

                status, response = player.play(action_obj, target)
                if not status:
                    print(response)
            except errors.ActionNotAllowed as e:
                print(e.message)
                return choose_action()
            except errors.NotEnoughCoins as exc:
                print(
                    f" You need {exc.coins_needed} coins to play {action_obj.name}. You only have {player.coins} coins."
                )
                return choose_action()
            except errors.BlockOnly:
                print(f"You cannot play {action_obj.name} as an action")
                return choose_action()
            except errors.TargetRequired:
                print("You need to select a valid target.\n")
                print_actions()
                return choose_action()

        if player.alive:
            print_info()
            print("\nAvailable actions:")
            print_actions()
            choose_action()

        cleanup()
        if game_is_running:
            input(
                f"\n{players[current_player].name}, press enter key to take your turn..."
            )

    if len(players_alive) == 1:
        clear_screen(f"The winner is {players_alive[0].name}", 79)


def main():
    clear_screen("Game Setup", 50)
    setup()

    for player in players:
        print_turn_order(player)

        input(f"\n{player.name}, press ENTER to see your cards")
        padding = " " * (len(player.name) + 2)
        held_cards = " and ".join(card.name for card in player.influence)
        print(f"\n{padding}{held_cards}\n")
        input(f"{padding}Press ENTER to hide your cards")

    clear_screen("Game start", 14)
    input(f"\n{players[0].name}, press enter key to start the game...")
    main_loop()


if __name__ == "__main__":
    main()
