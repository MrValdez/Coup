import unittest

from src.pycoup.core import action, errors
from src.pycoup.core.game import game_state
from src.pycoup.core.player import Player


class Actions(unittest.TestCase):
    def setUp(self):
        game_state.reset()
        game_state.PlayerList = []
        self.player = Player()

    def test_Income(self):
        player = self.player

        status, response = player.play(action.Income)
        self.assertEqual(player.coins, 3)

    def test_ForeignAid(self):
        player = self.player

        status, response = player.play(action.ForeignAid)
        self.assertEqual(player.coins, 4)

    def test_Coup(self):
        player = self.player
        player2 = Player()

        # test for no target
        player.coins = 7
        with self.assertRaises(errors.TargetRequired):
            status, response = player.play(action.Coup)

        # test for no player having insufficient money
        player.coins = 6
        with self.assertRaises(errors.NotEnoughCoins) as exc:
            status, response = player.play(action.Coup, player2)
        self.assertEqual(exc.exception.coinsNeeded, 7)

        # test for targetting self
        player.coins = 7
        with self.assertRaises(errors.TargetRequired):
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
        with self.assertRaises(errors.DeadPlayer):
            status, response = player.play(action.Coup, player2)

    def test_Duke(self):
        player = self.player

        status, response = player.play(action.Duke)
        self.assertEqual(player.coins, 5)

    def test_Captain(self):
        player = self.player
        player2 = Player()

        # test for no target
        with self.assertRaises(errors.TargetRequired):
            status, response = player.play(action.Captain)
        self.assertEqual(player.coins, 2)
        self.assertEqual(player2.coins, 2)

        # test for targeting self
        with self.assertRaises(errors.TargetRequired):
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

    def test_Contessa(self):
        player = self.player

        # using Contessa as an action
        with self.assertRaises(errors.BlockOnly):
            status, response = player.play(action.Contessa)

        # using Contessa as a block
        class BlockWithContessa(Player):
            def confirmBlock(self, activePlayer, opponentAction):
                return action.Contessa

        player2 = BlockWithContessa()

        player.coins = 3
        status, response = player.play(action.Assassin, player2)
        self.assertEqual(len(player2.influence), 2)

    def test_Assassin(self):
        player = self.player
        player2 = Player()

        # test for no player having insufficient money
        player.coins = 2
        self.assertEqual(len(player2.influence), 2)

        with self.assertRaises(errors.NotEnoughCoins) as exc:
            status, response = player.play(action.Assassin, player2)
        self.assertEqual(exc.exception.coinsNeeded, 3)
        self.assertEqual(len(player2.influence), 2)
        self.assertEqual(player.coins, 2)

        # test with sufficient money, no target
        player.coins = 3
        with self.assertRaises(errors.TargetRequired):
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

    def test_Ambassador(self):
        class AmbassadorTester(Player):
            def __init__(self, CardToPick):
                self.CardToPick = CardToPick
                Player.__init__(self)

            def selectAmbassadorInfluence(self, choices, influenceRemaining):
                return self.CardToPick

        # test with player having two influence
        player = AmbassadorTester([action.Duke, action.ForeignAid])
        player.influence = [action.Income, action.ForeignAid]
        game_state.Deck = [action.Duke, action.Ambassador]

        status, response = player.play(action.Ambassador)
        self.assertTrue(status, response)

        self.assertIn(action.Duke, player.influence)
        self.assertIn(action.ForeignAid, player.influence)
        self.assertIn(action.Income, game_state.Deck)
        self.assertIn(action.Ambassador, game_state.Deck)

        # test with player having one influence
        player = AmbassadorTester(action.Duke)
        player.influence = [action.Income]
        game_state.Deck = [action.Duke, action.Ambassador]

        status, response = player.play(action.Ambassador)
        self.assertIn(action.Duke, player.influence)
        self.assertIn(action.Income, game_state.Deck)
        self.assertIn(action.Ambassador, game_state.Deck)

        # test duplicates
        player = AmbassadorTester([action.Ambassador])
        player.influence = [action.Ambassador]
        game_state.Deck = [action.Ambassador, action.Ambassador]
        status, response = player.play(action.Ambassador)

        self.assertEqual(len(player.influence), 1)
        self.assertEqual(len(game_state.Deck), 2)
        self.assertEqual(player.influence[0], action.Ambassador)
        self.assertEqual(game_state.Deck[0], action.Ambassador)
        self.assertEqual(game_state.Deck[1], action.Ambassador)

        class AmbassadorCheaterTester(Player):
            def __init__(self, CardToPick):
                self.CardToPick = CardToPick
                Player.__init__(self)

            def selectAmbassadorInfluence(self, choices, influenceRemaining):
                return self.CardToPick

        # test with player cheating by selecting a card that is not in the choices
        player = AmbassadorCheaterTester([action.Contessa, action.Contessa])
        player.influence = [action.Income, action.ForeignAid]
        game_state.Deck = [action.Duke, action.Ambassador]
        with self.assertRaises(errors.InvalidTarget):
            status, response = player.play(action.Ambassador)

        # test with player cheating by having just one influence but selecting two
        player = AmbassadorCheaterTester([action.Duke, action.Ambassador])
        player.influence = [action.Income]
        game_state.Deck = [action.Duke, action.Ambassador]
        with self.assertRaises(errors.InvalidTarget):
            status, response = player.play(action.Ambassador)

    def test_Ambassador_ComplexScenario(self):
        # test where active player uses Ambassador, called by opponent, shows Ambassador,
        # removes one influence by the opponent, active player's Ambassador card is shuffled
        # into the deck, and the Ambassador action still passes
        class AmbassadorComplexTester(Player):
            def selectAmbassadorInfluence(self, choices, influenceRemaining):
                return [action.Duke, action.Duke]

        class AlwaysCallingPlayer(Player):
            def confirmCall(self, activePlayer, action):
                return True

        player = AmbassadorComplexTester()
        player.influence = [action.Ambassador, action.Duke]

        player2 = AlwaysCallingPlayer()
        player2.influence = [action.Ambassador, action.Duke]

        game_state.Deck = [action.Duke, action.Assassin]

        def randomShuffle(deck):
            pass  # does not shuffle

        def randomSelector(deck):
            return deck[0]  # select the first card in the deck

        # change the random functions used by the Game State so we can test
        game_state.randomShuffle = randomShuffle
        game_state.randomSelector = randomSelector

        status, response = player.play(action.Ambassador)
        self.assertTrue(status, response)

        self.assertEqual(len(player.influence), 2)
        self.assertEqual(len(player2.influence), 1)

        self.assertEqual(player.influence[0], action.Duke)
        self.assertEqual(player.influence[1], action.Duke)
        self.assertEqual(game_state.Deck[0], action.Assassin)
        self.assertEqual(game_state.Deck[1], action.Ambassador)


class Players(unittest.TestCase):
    def setUp(self):
        game_state.reset()
        game_state.PlayerList = []

        self.player = Player()

    def test_PlayerList(self):
        self.assertEqual(len(game_state.PlayerList), 1)
        self.assertIn(self.player, game_state.PlayerList)

    def test_PlayerInitialState(self):
        player = self.player

        self.assertEqual(player.coins, 2)
        self.assertTrue(player.alive)

    def test_DeadPlayerPlaying(self):
        """test to make sure a dead player can't play an action"""
        player = self.player
        player.alive = False

        with self.assertRaises(errors.DeadPlayer):
            status, response = player.play(action.Income)

    def test_DeadPlayerTarget(self):
        """test to make sure a dead player can't be targetted"""
        player = self.player
        player2 = Player()
        player2.alive = False

        with self.assertRaises(errors.DeadPlayer):
            status, response = player.play(action.Captain, player2)

    def test_CourtDeck(self):
        """
        Tests related to the court deck found in game_state class.
            Card Drawing
            Drawing card from an empty deck (should raise MajorError)
            Returning card to deck
        """
        game_state.Deck = [action.Income]
        card = game_state.DrawCard()

        self.assertEqual(len(game_state.Deck), 0)
        self.assertEqual(action.Income, card)

        with self.assertRaises(errors.MajorError):
            card = game_state.DrawCard()

        game_state.AddToDeck(action.ForeignAid)

        self.assertEqual(len(game_state.Deck), 1)
        self.assertIn(action.ForeignAid, game_state.Deck)

    def test_PlayerChangeCard(self):
        """
        Tests releated to the ChangeCard in Player class:
         - player has two influences
         - player has one influence
         - player has no influence
        """

        class FirstInfluenceDies(Player):
            def selectInfluenceToDie(self):
                return self.influence[0]

        player = FirstInfluenceDies()
        player.influence = [action.Income, action.ForeignAid]

        # changing card that is not in the player's influence.
        card = action.Duke
        with self.assertRaises(BaseException):
            player.changeCard(card)

        # drawing from an empty deck. In normal play, this will never happen, but is tested nonetheless
        game_state.Deck = []
        player.changeCard(action.Income)
        self.assertEqual(len(game_state.Deck), 0)

        # one card in the deck.
        game_state.Deck = [action.Duke]
        player.changeCard(action.Income)

        # because there's only one card in the deck, either the duke or income will be taken.
        # todo: add code to take over the rng for testing purposes
        self.assertTrue(
            (action.Duke in game_state.Deck) or (action.Income in game_state.Deck)
        )
        self.assertEqual(len(game_state.Deck), 1)

        game_state.Deck = [action.Duke]
        player.influence = [action.Income, action.ForeignAid]
        player.loseInfluence()
        self.assertEqual(len(player.influence), 1)
        self.assertTrue(player.influence[0] == action.ForeignAid)
        player.changeCard(player.influence[0])

        # because there's only one card in the deck, either the duke or income will be taken.
        # todo: add code to take over the rng for testing purposes
        self.assertTrue(
            (action.Duke in game_state.Deck) or (action.ForeignAid in game_state.Deck)
        )
        self.assertEqual(len(game_state.Deck), 1)

        # player should be dead
        player.loseInfluence()
        self.assertFalse(player.alive)
        self.assertEqual(len(player.influence), 0)
        with self.assertRaises(IndexError):
            player.changeCard(player.influence[0])

    def test_ForceCoup(self):
        player = self.player

        # test that player can't play any actions other than coup when holding more than action.ForceCoupCoins coins
        player.coins = action.ForceCoupCoins
        with self.assertRaises(errors.ActionNotAllowed):
            status, response = player.play(action.Income)
        self.assertEqual(player.coins, action.ForceCoupCoins)

        # test that player can play any actions other than coup when holding less than action.ForceCoupCoins coins
        player.coins = action.ForceCoupCoins - 1
        status, response = player.play(action.Income)
        self.assertTrue(status, response)
        self.assertEqual(player.coins, action.ForceCoupCoins)

        # test that dead players can't play any actions other than coup when holding more than action.ForceCoupCoins coins
        player.coins = action.ForceCoupCoins
        player.alive = False
        with self.assertRaises(errors.DeadPlayer):
            status, response = player.play(action.Income)
        self.assertEqual(player.coins, action.ForceCoupCoins)

    def test_RequestBlocksRotation(self):
        """
        This tests that requests are performed in a clockwise rotation (http://boardgamegeek.com/article/18425206#18425206).
        However, for the sake of game flow, the targetted player (if any) will be requested first.
        """
        game_state.reset()
        game_state.PlayerList = []

        Order = []

        class PlayerNumber(Player):
            def __init__(self, position, Order):
                self.position = position
                self.Order = Order
                Player.__init__(self)

            def confirmBlock(self, activePlayer, opponentAction):
                self.Order.append(self.position)
                return None

        _ = PlayerNumber(1, Order)
        _ = PlayerNumber(2, Order)
        player3 = PlayerNumber(3, Order)
        player4 = PlayerNumber(4, Order)
        _ = PlayerNumber(5, Order)
        _ = PlayerNumber(6, Order)

        status, response = player4.play(action.Captain, player3)
        self.assertTrue(status, response)

        self.assertEqual(Order, [3, 5, 6, 1, 2])

    def test_RequestCallsRotation(self):
        """
        This tests that requests are performed in a clockwise rotation (http://boardgamegeek.com/article/18425206#18425206).
        However, for the sake of game flow, the targetted player (if any) will be requested first.
        """
        game_state.reset()
        game_state.PlayerList = []

        Order = []

        class PlayerNumber(Player):
            def __init__(self, position, Order):
                self.position = position
                self.Order = Order
                Player.__init__(self)

            def confirmCall(self, activePlayer, action):
                self.Order.append(self.position)
                return False

        _ = PlayerNumber(1, Order)
        _ = PlayerNumber(2, Order)
        player3 = PlayerNumber(3, Order)
        player4 = PlayerNumber(4, Order)
        _ = PlayerNumber(5, Order)
        _ = PlayerNumber(6, Order)

        status, response = player4.play(action.Captain, player3)
        self.assertTrue(status, response)

        self.assertEqual(Order, [3, 5, 6, 1, 2])


class BlockingSystem(unittest.TestCase):
    def setUp(self):
        game_state.reset()
        game_state.PlayerList = []
        self.player = Player()

    class AlwaysBlockingPlayer(Player):
        def __init__(self, CardUsedToBlock):
            self.CardUsedToBlock = CardUsedToBlock
            Player.__init__(self)

        def confirmBlock(self, activePlayer, opponentAction):
            return self.CardUsedToBlock

    class NeverBlockingPlayer(Player):
        def confirmBlock(self, activePlayer, opponentAction):
            return None

    class AlwaysCallingPlayer(Player):
        def confirmCall(self, activePlayer, action):
            return True

    def test_getBlockingActions(self):
        # Foreign Aid
        blockers = game_state.getBlockingActions(action.ForeignAid)
        self.assertIn(action.Duke, blockers)

        # Captain
        blockers = game_state.getBlockingActions(action.Captain)
        self.assertIn(action.Captain, blockers)
        self.assertIn(action.Ambassador, blockers)

        # Assassin
        blockers = game_state.getBlockingActions(action.Assassin)
        self.assertIn(action.Contessa, blockers)

    def test_SelfBlocking(self):
        """Make sure that player can't block themselves"""
        player = BlockingSystem.AlwaysBlockingPlayer(action.ForeignAid)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertNotEqual(player.coins, 2)

    def test_BlockingAction(self):
        """Test if players can block"""
        # todo: use a mock object to create a mock action that is blockable

        player = self.player
        player_blocker = BlockingSystem.AlwaysBlockingPlayer(action.Duke)

        self.assertIn(player_blocker, game_state.PlayerList)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertEqual(player.coins, 2)

        self.assertFalse(status, response)
        expectedMessage = "Blocked by %s" % player_blocker.name
        self.assertEqual(response, expectedMessage)

    def test_BlockingAction_NoResponse(self):
        """Test if players can block"""
        # todo: use a mock object to create a mock action that is blockable
        player = self.player
        player_nonblocker = BlockingSystem.NeverBlockingPlayer()

        self.assertIn(player_nonblocker, game_state.PlayerList)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertEqual(player.coins, 4)

        self.assertTrue(status)

    def test_ValidBlockAction_Fail(self):
        """Only actions that can block active player's action can be used. This test checks that if an invalid block is used, nothing happens."""
        player = self.player
        _ = BlockingSystem.AlwaysBlockingPlayer(action.ForeignAid)

        self.assertEqual(player.coins, 2)
        status, _ = player.play(action.ForeignAid)
        self.assertEqual(player.coins, 4)
        self.assertTrue(status)

    def test_CallBlockingActionAsBluff_Success(self):
        """
        Opoosing player blocks action.
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

    def test_CallBlockingActionAsBluff_Fail(self):
        """
        Opoosing player blocks action.
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

    def test_CallBlockingActionAsBluffWithOneInfluence_Fail(self):
        """
        Opoosing player blocks action.
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

    def test_ChallengeFailAndPlayerShouldShuffleShownCard(self):
        """
        Create a scenario where active player plays action, opposing player calls bluff, active player is telling the truth.
        This will test that the active player's card is revealed, returned to the player deck and a new card is drawn.
        This will also test if after returning the card, the action still plays
        """
        # todo: use a mock object to create a mock action that is blockable

        player = self.player
        player.influence = [action.Income, action.Duke]
        player_caller = BlockingSystem.AlwaysCallingPlayer()

        def randomShuffle(deck):
            pass  # does not shuffle

        def randomSelector(deck):
            return deck[0]  # select the first card in the deck

        # change the random functions used by the Game State so we can test
        game_state.randomShuffle = randomShuffle
        game_state.randomSelector = randomSelector
        game_state.Deck = [action.Income]

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.Duke)
        self.assertTrue(status, response)
        self.assertEqual(player.coins, 5)

        self.assertEqual(len(player.influence), 2)
        self.assertEqual(len(player_caller.influence), 1)

        # check that the winner of the challenge draw from the deck.
        self.assertEqual(player.influence[0], action.Income)
        self.assertEqual(player.influence[1], action.Income)
        self.assertEqual(game_state.Deck[0], action.Duke)

    def test_PlayerIsBlockedAndChallengeFailAndBlockerShouldShuffleShownCard(self):
        """
        Create a scenario where active player plays action, opposing player blocks, active player calls and
        opposing player is telling the truth.
        This will test that the blocking player's card is revealed, returned to the player deck and a new card is drawn.
        This will also test if after returning the card, the action is still blocked
        """
        # todo: use a mock object to create a mock action that is blockable

        player = BlockingSystem.AlwaysCallingPlayer()
        player.influence = [action.Captain, action.Captain]
        player_blocker = BlockingSystem.AlwaysBlockingPlayer(action.Captain)
        player_blocker.influence = [action.Captain, action.Duke]

        def randomShuffle(deck):
            pass  # does not shuffle

        def randomSelector(deck):
            return deck[0]  # select the first card in the deck

        # change the random functions used by the Game State so we can test
        game_state.randomShuffle = randomShuffle
        game_state.randomSelector = randomSelector
        game_state.Deck = [action.Duke]

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.Captain, player_blocker)
        self.assertFalse(status, response)
        self.assertEqual(player.coins, 2)

        self.assertEqual(len(player.influence), 1)
        self.assertEqual(len(player_blocker.influence), 2)

        # check that the winner of the challenge draw from the deck.
        self.assertEqual(player.influence[0], action.Captain)
        self.assertEqual(player_blocker.influence[0], action.Duke)
        self.assertEqual(player_blocker.influence[1], action.Duke)
        self.assertEqual(game_state.Deck[0], action.Captain)

    class PlayerCallToLoseAndCannotBlock(Player):
        """For testing of complex scenario in test_BlockingPlayerBluffIsCalledAndTheyLoseGame()"""

        def confirmCall(self, activePlayer, action):
            return True

        def confirmBlock(self, activePlayer, opponentAction):
            raise errors.DeadPlayer

    def test_PlayerCallToLoseAndCannotBlock(self):
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
        # errors.DeadPlayer should never be called. If it does, then step #4 of this scenario happened


class ActionBlocking(unittest.TestCase):
    def setUp(self):
        game_state.reset()
        game_state.PlayerList = []
        self.player = Player()

    class AlwaysBlockingPlayer(Player):
        def __init__(self, CardUsedToBlock):
            self.CardUsedToBlock = CardUsedToBlock
            Player.__init__(self)

        def confirmBlock(self, activePlayer, opponentAction):
            return self.CardUsedToBlock

    class NeverBlockingPlayer(Player):
        def confirmBlock(self, activePlayer, opponentAction):
            return None

    class AlwaysCallingPlayer(Player):
        def confirmCall(self, activePlayer, action):
            return True

    def test_ForeignAid(self):
        """Test for players blocking foriegn aid"""
        # todo: use a mock object to create a mock action that is blockable
        player = self.player
        _ = ActionBlocking.AlwaysBlockingPlayer(action.Duke)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertFalse(status, response)
        self.assertEqual(player.coins, 2)

    def test_Captain(self):
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
        game_state.PlayerList = []
        self.player = Player()

    class AlwaysCallingPlayer(Player):
        def confirmCall(self, activePlayer, action):
            return True

    class AlwaysBlockingPlayer(Player):
        def __init__(self, CardUsedToBlock):
            self.CardUsedToBlock = CardUsedToBlock
            Player.__init__(self)

        def confirmBlock(self, activePlayer, opponentAction):
            return self.CardUsedToBlock

    def test_SelfCalling(self):
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

    def test_CallCommonAction(self):
        """Test to make sure that players shouldn't be able to call common actions as bluffs"""
        player = self.player
        player.giveCards(action.ForeignAid)  # todo: add mock object for action

        _ = CallBluff.AlwaysCallingPlayer()

        playedAction = action.Income
        self.assertEqual(player.coins, 2)
        _, _ = player.play(playedAction)
        self.assertEqual(player.coins, 3)

    def test_CallActivePlayerBluff_Success(self):
        """Test if other players can call active player's bluff"""
        player = self.player
        player.giveCards(action.Income)  # todo: add mock object for action
        self.assertEqual(len(player.influence), 2)

        player_CallBluff = CallBluff.AlwaysCallingPlayer()

        playedAction = action.Captain
        self.assertEqual(player.coins, 2)
        status, response = player.play(playedAction, player_CallBluff)
        self.assertEqual(player.coins, 2)

        self.assertEqual(len(player.influence), 1)
        self.assertFalse(status, response)
        expectedMessage = "Bluffing %s failed for %s" % (playedAction.name, player.name)
        self.assertEqual(response, expectedMessage)

    def test_CallActivePlayerBluff_Failed(self):
        """Test if other players can call active player's bluff"""
        player = self.player
        player.giveCards(action.ForeignAid)
        self.assertEqual(len(player.influence), 2)

        _ = CallBluff.AlwaysCallingPlayer()

        playedAction = action.ForeignAid
        self.assertEqual(player.coins, 2)
        status, _ = player.play(playedAction)
        self.assertEqual(player.coins, 4)

        self.assertEqual(len(player.influence), 2)
        self.assertTrue(status)

    def test_Assasinate_FailedContessaBluff(self):
        """Important rule test: An assasination attempt is done to opponent. Opponent bluff with Contessa. Active player calls bluff. The opposing player should lose. This will test for situations where the opposing player has two or one influence"""

        class ContessaBluffer(Player):
            def confirmBlock(self, activePlayer, opponentAction):
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

    def test_Assassin_FailedAssasinBluff(self):
        """Important rule test: A player bluffs assassin. Opponent calls bluff. The active player should lose a card but should not use up their coins."""
        player = self.player
        player.influence = [action.Income, action.Income]
        player.coins = 3

        player_CallBluff = CallBluff.AlwaysCallingPlayer()

        playedAction = action.Assassin
        status, response = player.play(playedAction, player_CallBluff)
        self.assertEqual(player.coins, 3)

        self.assertEqual(len(player.influence), 1)
        self.assertFalse(status)

        expectedMessage = "Bluffing %s failed for %s" % (playedAction.name, player.name)
        self.assertEqual(response, expectedMessage)


if __name__ == "__main__":
    unittest.main()
