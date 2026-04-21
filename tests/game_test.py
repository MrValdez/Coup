import unittest

from src.pycoup.core import action, errors
from src.pycoup.core.game import game_state
from src.pycoup.core.player import Player


class Actions(unittest.TestCase):
    def setUp(self):
        game_state.reset()
        game_state.player_list = []
        self.player = Player()

    def test_income(self):
        player = self.player

        status, response = player.play(action.Income)
        self.assertEqual(player.coins, 3)

    def test_foreign_aid(self):
        player = self.player

        status, response = player.play(action.ForeignAid)
        self.assertEqual(player.coins, 4)

    def test_coup(self):
        player = self.player
        player2 = Player()

        # test for no target
        player.coins = 7
        with self.assertRaises(errors.TargetRequiredError):
            status, response = player.play(action.Coup)

        # test for no player having insufficient money
        player.coins = 6
        with self.assertRaises(errors.NotEnoughCoinsError) as exc:
            status, response = player.play(action.Coup, player2)
        self.assertEqual(exc.exception.coins_needed, 7)

        # test for targetting self
        player.coins = 7
        with self.assertRaises(errors.TargetRequiredError):
            status, response = player.play(action.Coup, player)

        # test for succesful coup with opponent has 2 influence
        player2.alive = True
        player.coins = 7
        status, response = player.play(action.Coup, player2)
        self.assertTrue(status, response)
        self.assertLess(player.coins, 7)
        self.assertEqual(len(player2.influence), 1)
        self.assertTrue(player2.alive)

        # test for succesful coup with opponent has 1 influence
        player2.alive = True
        player.coins = 7
        self.assertEqual(len(player2.influence), 1)
        status, response = player.play(action.Coup, player2)
        self.assertTrue(status, response)
        self.assertLess(player.coins, 7)
        self.assertEqual(len(player2.influence), 0)
        self.assertFalse(player2.alive)

        # test for coup against dead opponent
        player2.alive = False
        player.coins = 7
        with self.assertRaises(errors.DeadPlayerError):
            status, response = player.play(action.Coup, player2)

    def test_duke(self):
        player = self.player

        status, response = player.play(action.Duke)
        self.assertEqual(player.coins, 5)

    def test_captain(self):
        player = self.player
        player2 = Player()

        # test for no target
        with self.assertRaises(errors.TargetRequiredError):
            status, response = player.play(action.Captain)
        self.assertEqual(player.coins, 2)
        self.assertEqual(player2.coins, 2)

        # test for targeting self
        with self.assertRaises(errors.TargetRequiredError):
            status, response = player.play(action.Captain, player)

        # test for steal from player 2
        player.play(action.Captain, player2)
        self.assertEqual(player.coins, 4)
        self.assertEqual(player2.coins, 0)

        # test for steal with only one coin
        player2.coins = 1
        player.play(action.Captain, player2)
        self.assertEqual(player.coins, 5)
        self.assertEqual(player2.coins, 0)

    def test_contessa(self):
        player = self.player

        # using Contessa as an action
        with self.assertRaises(errors.BlockOnlyError):
            status, response = player.play(action.Contessa)

        # using Contessa as a block
        class BlockWithContessa(Player):
            def confirm_block(self, active_player, opponent_action):
                return action.Contessa

        player2 = BlockWithContessa()

        player.coins = 3
        status, response = player.play(action.Assassin, player2)
        self.assertEqual(len(player2.influence), 2)

    def test_assassin(self):
        player = self.player
        player2 = Player()

        # test for no player having insufficient money
        player.coins = 2
        self.assertEqual(len(player2.influence), 2)

        with self.assertRaises(errors.NotEnoughCoinsError) as exc:
            status, response = player.play(action.Assassin, player2)
        self.assertEqual(exc.exception.coins_needed, 3)
        self.assertEqual(len(player2.influence), 2)
        self.assertEqual(player.coins, 2)

        # test with sufficient money, no target
        player.coins = 3
        with self.assertRaises(errors.TargetRequiredError):
            status, response = player.play(action.Assassin)
        self.assertEqual(len(player2.influence), 2)

        # test with sufficient money against player with 2 influences
        self.assertEqual(player.coins, 3)
        status, response = player.play(action.Assassin, player2)
        self.assertEqual(player.coins, 0)
        self.assertEqual(len(player2.influence), 1)

        # test with sufficient money against 1 influence and killing them
        player.coins = 3
        status, response = player.play(action.Assassin, player2)
        self.assertEqual(player.coins, 0)
        self.assertEqual(len(player2.influence), 0)
        self.assertFalse(player2.alive)

    def test_ambassador(self):
        class AmbassadorTester(Player):
            def __init__(self, card_to_pick):
                self.card_to_pick = card_to_pick
                super().__init__()

            def select_ambassador_influence(self, choices, influence_remaining):
                return self.card_to_pick

        # test with player having two influence
        player = AmbassadorTester([action.Duke, action.ForeignAid])
        player.influence = [action.Income, action.ForeignAid]
        game_state.deck = [action.Duke, action.Ambassador]

        status, response = player.play(action.Ambassador)
        self.assertTrue(status, response)

        self.assertIn(action.Duke, player.influence)
        self.assertIn(action.ForeignAid, player.influence)
        self.assertIn(action.Income, game_state.deck)
        self.assertIn(action.Ambassador, game_state.deck)

        # test with player having one influence
        player = AmbassadorTester(action.Duke)
        player.influence = [action.Income]
        game_state.deck = [action.Duke, action.Ambassador]

        status, response = player.play(action.Ambassador)
        self.assertIn(action.Duke, player.influence)
        self.assertIn(action.Income, game_state.deck)
        self.assertIn(action.Ambassador, game_state.deck)

        # test duplicates
        player = AmbassadorTester([action.Ambassador])
        player.influence = [action.Ambassador]
        game_state.deck = [action.Ambassador, action.Ambassador]
        status, response = player.play(action.Ambassador)

        self.assertEqual(len(player.influence), 1)
        self.assertEqual(len(game_state.deck), 2)
        self.assertEqual(player.influence[0], action.Ambassador)
        self.assertEqual(game_state.deck[0], action.Ambassador)
        self.assertEqual(game_state.deck[1], action.Ambassador)

        class AmbassadorCheaterTester(Player):
            def __init__(self, card_to_pick):
                self.card_to_pick = card_to_pick
                super().__init__()

            def select_ambassador_influence(self, choices, influence_remaining):
                return self.card_to_pick

        # test with player cheating by selecting a card that is not in the choices
        player = AmbassadorCheaterTester([action.Contessa, action.Contessa])
        player.influence = [action.Income, action.ForeignAid]
        game_state.deck = [action.Duke, action.Ambassador]
        with self.assertRaises(errors.InvalidTargetError):
            status, response = player.play(action.Ambassador)

        # test with player cheating by having just one influence but selecting two
        player = AmbassadorCheaterTester([action.Duke, action.Ambassador])
        player.influence = [action.Income]
        game_state.deck = [action.Duke, action.Ambassador]
        with self.assertRaises(errors.InvalidTargetError):
            status, response = player.play(action.Ambassador)

    def test_ambassador_complex_scenario(self):
        # test where active player uses Ambassador, called by opponent, shows Ambassador,
        # removes one influence by the opponent, active player's Ambassador card is shuffled
        # into the deck, and the Ambassador action still passes
        class AmbassadorComplexTester(Player):
            def select_ambassador_influence(self, choices, influence_remaining):
                return [action.Duke, action.Duke]

        class AlwaysCallingPlayer(Player):
            def confirm_call(self, active_player, action):
                return True

        player = AmbassadorComplexTester()
        player.influence = [action.Ambassador, action.Duke]

        player2 = AlwaysCallingPlayer()
        player2.influence = [action.Ambassador, action.Duke]

        game_state.deck = [action.Duke, action.Assassin]

        def random_shuffle(deck):
            pass  # does not shuffle

        def random_selector(deck):
            return deck[0]  # select the first card in the deck

        # change the random functions used by the Game State so we can test
        game_state.random_shuffle = random_shuffle
        game_state.random_selector = random_selector

        status, response = player.play(action.Ambassador)
        self.assertTrue(status, response)

        self.assertEqual(len(player.influence), 2)
        self.assertEqual(len(player2.influence), 1)

        self.assertEqual(player.influence[0], action.Duke)
        self.assertEqual(player.influence[1], action.Duke)
        self.assertEqual(game_state.deck[0], action.Assassin)
        self.assertEqual(game_state.deck[1], action.Ambassador)


class Players(unittest.TestCase):
    def setUp(self):
        game_state.reset()
        game_state.player_list = []

        self.player = Player()

    def test_player_list(self):
        self.assertEqual(len(game_state.player_list), 1)
        self.assertIn(self.player, game_state.player_list)

    def test_player_initial_state(self):
        player = self.player

        self.assertEqual(player.coins, 2)
        self.assertTrue(player.alive)

    def test_dead_player_playing(self):
        """test to make sure a dead player can't play an action"""
        player = self.player
        player.alive = False

        with self.assertRaises(errors.DeadPlayerError):
            status, response = player.play(action.Income)

    def test_dead_player_target(self):
        """test to make sure a dead player can't be targetted"""
        player = self.player
        player2 = Player()
        player2.alive = False

        with self.assertRaises(errors.DeadPlayerError):
            status, response = player.play(action.Captain, player2)

    def test_court_deck(self):
        """
        Tests related to the court deck found in game_state class.
            Card Drawing
            Drawing card from an empty deck (should raise MajorError)
            Returning card to deck
        """
        game_state.deck = [action.Income]
        card = game_state.draw_card()

        self.assertEqual(len(game_state.deck), 0)
        self.assertEqual(action.Income, card)

        with self.assertRaises(errors.MajorError):
            card = game_state.draw_card()

        game_state.add_to_deck(action.ForeignAid)

        self.assertEqual(len(game_state.deck), 1)
        self.assertIn(action.ForeignAid, game_state.deck)

    def test_player_change_card(self):
        """
        Tests releated to the ChangeCard in Player class:
         - player has two influences
         - player has one influence
         - player has no influence
        """

        class FirstInfluenceDies(Player):
            def select_influence_to_die(self):
                return self.influence[0]

        player = FirstInfluenceDies()
        player.influence = [action.Income, action.ForeignAid]

        # changing card that is not in the player's influence.
        card = action.Duke
        with self.assertRaises(BaseException):
            player.change_card(card)

        # drawing from an empty deck. In normal play, this will never happen, but is tested nonetheless
        game_state.deck = []
        player.change_card(action.Income)
        self.assertEqual(len(game_state.deck), 0)

        # one card in the deck.
        game_state.deck = [action.Duke]
        player.change_card(action.Income)

        # because there's only one card in the deck, either the duke or income will be taken.
        # todo: add code to take over the rng for testing purposes
        self.assertTrue(
            (action.Duke in game_state.deck) or (action.Income in game_state.deck)
        )
        self.assertEqual(len(game_state.deck), 1)

        game_state.deck = [action.Duke]
        player.influence = [action.Income, action.ForeignAid]
        player.lose_influence()
        self.assertEqual(len(player.influence), 1)
        self.assertTrue(player.influence[0] == action.ForeignAid)
        player.change_card(player.influence[0])

        # because there's only one card in the deck, either the duke or income will be taken.
        # todo: add code to take over the rng for testing purposes
        self.assertTrue(
            (action.Duke in game_state.deck) or (action.ForeignAid in game_state.deck)
        )
        self.assertEqual(len(game_state.deck), 1)

        # player should be dead
        player.lose_influence()
        self.assertFalse(player.alive)
        self.assertEqual(len(player.influence), 0)
        with self.assertRaises(IndexError):
            player.change_card(player.influence[0])

    def test_force_coup(self):
        player = self.player

        # test that player can't play any actions other than coup when holding more than action.FORCE_COUP_COINS coins
        player.coins = action.FORCE_COUP_COINS
        with self.assertRaises(errors.ActionNotAllowedError):
            status, response = player.play(action.Income)
        self.assertEqual(player.coins, action.FORCE_COUP_COINS)

        # test that player can play any actions other than coup when holding less than action.FORCE_COUP_COINS coins
        player.coins = action.FORCE_COUP_COINS - 1
        status, response = player.play(action.Income)
        self.assertTrue(status, response)
        self.assertEqual(player.coins, action.FORCE_COUP_COINS)

        # test that dead players can't play any actions other than coup when holding more than action.FORCE_COUP_COINS coins
        player.coins = action.FORCE_COUP_COINS
        player.alive = False
        with self.assertRaises(errors.DeadPlayerError):
            status, response = player.play(action.Income)
        self.assertEqual(player.coins, action.FORCE_COUP_COINS)

    def test_request_blocks_rotation(self):
        """
        This tests that requests are performed in a clockwise rotation (http://boardgamegeek.com/article/18425206#18425206).
        However, for the sake of game flow, the targetted player (if any) will be requested first.
        """
        game_state.reset()
        game_state.player_list = []

        order = []

        class PlayerNumber(Player):
            def __init__(self, position, order):
                self.position = position
                self.order = order
                super().__init__()

            def confirm_block(self, active_player, opponent_action):
                self.order.append(self.position)
                return None

        _ = PlayerNumber(1, order)
        _ = PlayerNumber(2, order)
        player3 = PlayerNumber(3, order)
        player4 = PlayerNumber(4, order)
        _ = PlayerNumber(5, order)
        _ = PlayerNumber(6, order)

        status, response = player4.play(action.Captain, player3)
        self.assertTrue(status, response)

        self.assertEqual(order, [3, 5, 6, 1, 2])

    def test_request_calls_rotation(self):
        """
        This tests that requests are performed in a clockwise rotation (http://boardgamegeek.com/article/18425206#18425206).
        However, for the sake of game flow, the targetted player (if any) will be requested first.
        """
        game_state.reset()
        game_state.player_list = []

        order = []

        class PlayerNumber(Player):
            def __init__(self, position, order):
                self.position = position
                self.order = order
                super().__init__()

            def confirm_call(self, active_player, action):
                self.order.append(self.position)
                return False

        _ = PlayerNumber(1, order)
        _ = PlayerNumber(2, order)
        player3 = PlayerNumber(3, order)
        player4 = PlayerNumber(4, order)
        _ = PlayerNumber(5, order)
        _ = PlayerNumber(6, order)

        status, response = player4.play(action.Captain, player3)
        self.assertTrue(status, response)

        self.assertEqual(order, [3, 5, 6, 1, 2])


class BlockingSystem(unittest.TestCase):
    def setUp(self):
        game_state.reset()
        game_state.player_list = []
        self.player = Player()

    class AlwaysBlockingPlayer(Player):
        def __init__(self, card_used_to_block):
            self.card_used_to_block = card_used_to_block
            super().__init__()

        def confirm_block(self, active_player, opponent_action):
            return self.card_used_to_block

    class NeverBlockingPlayer(Player):
        def confirm_block(self, active_player, opponent_action):
            return None

    class AlwaysCallingPlayer(Player):
        def confirm_call(self, active_player, action):
            return True

    def test_get_blocking_actions(self):
        # Foreign Aid
        blockers = game_state.get_blocking_actions(action.ForeignAid)
        self.assertIn(action.Duke, blockers)

        # Captain
        blockers = game_state.get_blocking_actions(action.Captain)
        self.assertIn(action.Captain, blockers)
        self.assertIn(action.Ambassador, blockers)

        # Assassin
        blockers = game_state.get_blocking_actions(action.Assassin)
        self.assertIn(action.Contessa, blockers)

    def test_self_blocking(self):
        """Make sure that player can't block themselves"""
        player = BlockingSystem.AlwaysBlockingPlayer(action.ForeignAid)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertTrue(status, response)
        self.assertEqual(player.coins, 4)

    def test_blocking_action(self):
        """Test if players can block"""
        # todo: use a mock object to create a mock action that is blockable

        player = self.player
        player_blocker = BlockingSystem.AlwaysBlockingPlayer(action.Duke)

        self.assertIn(player_blocker, game_state.player_list)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertEqual(player.coins, 2)

        self.assertFalse(status, response)
        expected_message = f"Blocked by {player_blocker.name}"
        self.assertEqual(response, expected_message)

    def test_blocking_action_no_response(self):
        """Test if players can block"""
        # todo: use a mock object to create a mock action that is blockable
        player = self.player
        player_nonblocker = BlockingSystem.NeverBlockingPlayer()

        self.assertIn(player_nonblocker, game_state.player_list)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertEqual(player.coins, 4)

        self.assertTrue(status)

    def test_valid_block_action_fail(self):
        """Only actions that can block active player's action can be used. This test checks that if an invalid block is used, nothing happens."""
        player = self.player
        _ = BlockingSystem.AlwaysBlockingPlayer(action.ForeignAid)

        self.assertEqual(player.coins, 2)
        status, _ = player.play(action.ForeignAid)
        self.assertEqual(player.coins, 4)
        self.assertTrue(status)

    def test_call_blocking_action_as_bluff_success(self):
        """
        Opposing player blocks action.
        Active player calls bluff.
        Opposing player is bluffing and should lose influence.
        The active player's action should succeed.
        """
        # todo: use a mock object to create a mock action that is blockable

        player = BlockingSystem.AlwaysCallingPlayer()
        player_blocker = BlockingSystem.AlwaysBlockingPlayer(action.Duke)
        player_blocker.influence = [action.Income, action.Income]

        self.assertEqual(len(player.influence), 2)
        self.assertEqual(len(player_blocker.influence), 2)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertTrue(status)
        self.assertEqual(player.coins, 4)

        self.assertEqual(len(player.influence), 2)
        self.assertEqual(len(player_blocker.influence), 1)

    def test_call_blocking_action_as_bluff_fail(self):
        """
        Opposing player blocks action.
        Active player calls bluff.
        Opposing player is telling the truth. Their card should be shuffled back and active player should lose influence.
        The action should fail.
        """
        # todo: use a mock object to create a mock action that is blockable

        player = BlockingSystem.AlwaysCallingPlayer()
        player_blocker = BlockingSystem.AlwaysBlockingPlayer(action.Duke)
        player_blocker.influence = [action.Duke, action.Duke]

        self.assertEqual(len(player.influence), 2)
        self.assertEqual(len(player_blocker.influence), 2)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertFalse(status)
        self.assertEqual(player.coins, 2)

        self.assertEqual(len(player.influence), 1)
        self.assertEqual(len(player_blocker.influence), 2)

    def test_call_blocking_action_as_bluff_with_one_influence_fail(self):
        """
        Opposing player blocks action.
        Active player, with one influence, calls bluff.
        Opposing player is telling the truth. Their card should be shuffled back and active player should loses the game.
        The action should fail.
        """
        # todo: use a mock object to create a mock action that is blockable

        player = BlockingSystem.AlwaysCallingPlayer()
        player.influence = [action.Duke]
        player_blocker = BlockingSystem.AlwaysBlockingPlayer(action.Duke)
        player_blocker.influence = [action.Duke, action.Duke]

        self.assertEqual(len(player.influence), 1)
        self.assertEqual(len(player_blocker.influence), 2)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertFalse(status)
        self.assertEqual(player.coins, 2)

        self.assertFalse(player.alive)
        self.assertEqual(len(player.influence), 0)
        self.assertEqual(len(player_blocker.influence), 2)

    def test_challenge_fail_and_player_should_shuffle_shown_card(self):
        """
        Create a scenario where active player plays action, opposing player calls bluff, active player is telling the truth.
        This will test that the active player's card is revealed, returned to the player deck and a new card is drawn.
        This will also test if after returning the card, the action still plays
        """
        player = self.player
        player.influence = [action.Income, action.Duke]
        player_caller = BlockingSystem.AlwaysCallingPlayer()

        def random_shuffle(deck):
            pass  # does not shuffle

        def random_selector(deck):
            return deck[0]  # select the first card in the deck

        # change the random functions used by the Game State so we can test
        game_state.random_shuffle = random_shuffle
        game_state.random_selector = random_selector
        game_state.deck = [action.Income]

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.Duke)
        self.assertTrue(status, response)
        self.assertEqual(player.coins, 5)

        self.assertEqual(len(player.influence), 2)
        self.assertEqual(len(player_caller.influence), 1)

        # check that the winner of the challenge draw from the deck.
        self.assertEqual(player.influence[0], action.Income)
        self.assertEqual(player.influence[1], action.Income)
        self.assertEqual(game_state.deck[0], action.Duke)

    def test_player_is_blocked_and_challenge_fail_and_blocker_should_shuffle_shown_card(
        self,
    ):
        """
        Create a scenario where active player plays action, opposing player blocks, active player calls and
        opposing player is telling the truth.
        This will test that the blocking player's card is revealed, returned to the player deck and a new card is drawn.
        This will also test if after returning the card, the action is still blocked
        """
        player = BlockingSystem.AlwaysCallingPlayer()
        player.influence = [action.Captain, action.Captain]
        player_blocker = BlockingSystem.AlwaysBlockingPlayer(action.Captain)
        player_blocker.influence = [action.Captain, action.Duke]

        def random_shuffle(deck):
            pass  # does not shuffle

        def random_selector(deck):
            return deck[0]  # select the first card in the deck

        # change the random functions used by the Game State so we can test
        game_state.random_shuffle = random_shuffle
        game_state.random_selector = random_selector
        game_state.deck = [action.Duke]

        # blocker blocks with Captain, active player calls bluff, blocker tells truth and active player loses influence
        status, response = player.play(action.Captain, player_blocker)
        self.assertFalse(status, response)
        self.assertEqual(len(player.influence), 1)
        self.assertEqual(len(player_blocker.influence), 2)

        # check that the winner of the challenge draw from the deck.
        self.assertEqual(player.influence[0], action.Captain)
        self.assertEqual(player_blocker.influence[0], action.Duke)
        self.assertEqual(player_blocker.influence[1], action.Duke)
        self.assertEqual(game_state.deck[0], action.Captain)

    class PlayerCallToLoseAndCannotBlock(Player):
        """For testing of complex scenario in test_blocking_player_bluff_is_called_and_they_lose_game()"""

        def confirm_call(self, active_player, action):
            return True

        def confirm_block(self, active_player, opponent_action):
            raise errors.DeadPlayerError

    def test_player_call_to_lose_and_cannot_block(self):
        """
        This test the following scenario:
            1. Active player plays an action
            2. Another player calls bluff but active player is telling the truth
            3. Blocking player loses their last influence
            4. Blocking player SHOULD NOT get the ability to block active player's action
        """
        player = BlockingSystem.AlwaysCallingPlayer()
        player_blocker = BlockingSystem.PlayerCallToLoseAndCannotBlock()
        player.influence = [action.Captain, action.Captain]
        player_blocker.influence = [action.Duke]

        self.assertEqual(len(player_blocker.influence), 1)
        status, response = player.play(action.Captain, player_blocker)
        self.assertEqual(len(player_blocker.influence), 0)
        self.assertFalse(player_blocker.alive)
        # errors.DeadPlayerError should never be called. If it does, then step #4 of this scenario happened


class ActionBlocking(unittest.TestCase):
    def setUp(self):
        game_state.reset()
        game_state.player_list = []
        self.player = Player()

    class AlwaysBlockingPlayer(Player):
        def __init__(self, card_used_to_block):
            self.card_used_to_block = card_used_to_block
            super().__init__()

        def confirm_block(self, active_player, opponent_action):
            return self.card_used_to_block

    class NeverBlockingPlayer(Player):
        def confirm_block(self, active_player, opponent_action):
            return None

    class AlwaysCallingPlayer(Player):
        def confirm_call(self, active_player, action):
            return True

    def test_foreign_aid(self):
        """Test for players blocking foreign aid"""
        # todo: use a mock object to create a mock action that is blockable
        player = self.player
        _ = ActionBlocking.AlwaysBlockingPlayer(action.Duke)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertFalse(status, response)
        self.assertEqual(player.coins, 2)

    def test_captain(self):
        """Test for players blocking stealing"""
        # todo: use a mock object to create a mock action that is blockable
        player = self.player
        player_blocker = ActionBlocking.AlwaysBlockingPlayer(action.Captain)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.Captain, player_blocker)
        self.assertFalse(status, response)
        self.assertEqual(player.coins, 2)

    # todo: add tests for all cards


class CallBluff(unittest.TestCase):
    def setUp(self):
        game_state.reset()
        game_state.player_list = []
        self.player = Player()

    class AlwaysCallingPlayer(Player):
        def confirm_call(self, active_player, action):
            return True

    class AlwaysBlockingPlayer(Player):
        def __init__(self, card_used_to_block):
            self.card_used_to_block = card_used_to_block
            super().__init__()

        def confirm_block(self, active_player, opponent_action):
            return self.card_used_to_block

    def test_self_calling(self):
        """Make sure that player can't call themselves as bluffers"""

        class GenericCardThatCanBlockItself(action.Action):
            name = "Generic Card That Can Block Itelf"
            description = "For testing purposes"

            def play(self, player, target=None):
                player.coins += 1
                return True, "Success"

        player = CallBluff.AlwaysBlockingPlayer(GenericCardThatCanBlockItself)

        self.assertEqual(player.coins, 2)
        status, response = player.play(GenericCardThatCanBlockItself)
        self.assertTrue(status)
        self.assertEqual(player.coins, 3)

    def test_call_common_action(self):
        """Test to make sure that players shouldn't be able to call common actions as bluffs"""
        player = self.player
        player.give_cards(action.ForeignAid)

        _ = CallBluff.AlwaysCallingPlayer()

        played_action = action.Income
        self.assertEqual(player.coins, 2)
        _, _ = player.play(played_action)
        self.assertEqual(player.coins, 3)

    def test_call_active_player_bluff_success(self):
        """Test if other players can call active player's bluff"""
        player = self.player
        player.give_cards(action.Income)
        self.assertEqual(len(player.influence), 2)

        player_call_bluff = CallBluff.AlwaysCallingPlayer()

        played_action = action.Captain
        self.assertEqual(player.coins, 2)
        status, response = player.play(played_action, player_call_bluff)
        self.assertEqual(player.coins, 2)

        self.assertEqual(len(player.influence), 1)
        self.assertFalse(status, response)
        expected_message = f"Bluffing {played_action.name} failed for {player.name}"
        self.assertEqual(response, expected_message)

    def test_call_active_player_bluff_failed(self):
        """Test if other players can call active player's bluff"""
        player = self.player
        player.give_cards(action.ForeignAid)
        self.assertEqual(len(player.influence), 2)

        _ = CallBluff.AlwaysCallingPlayer()

        played_action = action.ForeignAid
        self.assertEqual(player.coins, 2)
        status, _ = player.play(played_action)
        self.assertEqual(player.coins, 4)

        self.assertEqual(len(player.influence), 2)
        self.assertTrue(status)

    def test_assasinate_failed_contessa_bluff(self):
        """Important rule test: An assasination attempt is done to opponent. Opponent bluff with Contessa. Active player calls bluff. The opposing player should lose. This will test for situations where the opposing player has two or one influence"""

        class ContessaBluffer(Player):
            def confirm_block(self, active_player, opponent_action):
                return action.Contessa

        player = CallBluff.AlwaysCallingPlayer()
        player2 = ContessaBluffer()
        player2.influence = [action.Income, action.Income]

        self.assertEqual(len(player2.influence), 2)
        self.assertTrue(player2.alive)

        player.coins = 3
        status, response = player.play(action.Assassin, player2)
        self.assertEqual(player.coins, 0)

        self.assertEqual(len(player2.influence), 0)

    def test_assassin_failed_assasin_bluff(self):
        """Important rule test: A player bluffs assassin. Opponent calls bluff. The active player should lose a card but should not use up their coins."""
        player = self.player
        player.influence = [action.Income, action.Income]
        player.coins = 3

        player_call_bluff = CallBluff.AlwaysCallingPlayer()

        played_action = action.Assassin
        status, response = player.play(played_action, player_call_bluff)
        self.assertEqual(player.coins, 3)

        self.assertEqual(len(player.influence), 1)
        self.assertFalse(status)

        expected_message = f"Bluffing {played_action.name} failed for {player.name}"
        self.assertEqual(response, expected_message)


if __name__ == "__main__":
    unittest.main()
