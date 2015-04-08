import unittest
import action
from player import Player
from game   import GameState

class Actions(unittest.TestCase):
    def setUp(self):
        GameState.PlayerList = []
        self.player = Player()

    def tearDown(self):
        GameState.reset()
        
    def test_Income(self):
        player = self.player
        
        player.play(action.Income)
        self.assertEqual(player.coins, 3)
            
    def test_ForeignAid(self):
        player = self.player
        
        player.play(action.ForeignAid)
        self.assertEqual(player.coins, 4)
    
    def test_Coup(self):
        player  = self.player
        player2 = Player()
        
        # test for no target
        status, response = player.play(action.Coup)
        self.assertFalse(status, response)

        # test for no player having insufficient money
        player.coins = 6
        status, response = player.play(action.Coup, player2)
        self.assertFalse(status, response)
        
        # test for target being dead
        player2.alive = False
        status, response = player.play(action.Coup, player2)
        self.assertFalse(status, response)
        
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
                
    def test_Duke(self):
        player = self.player
        
        player.play(action.Duke)
        self.assertEqual(player.coins, 5)

class Players(unittest.TestCase):
    def setUp(self):
        GameState.PlayerList = []
        
        self.player = Player()

    def tearDown(self):
        GameState.reset()

    def test_PlayerList(self):
        self.assertEqual(len(GameState.PlayerList), 1)
        self.assertIn(self.player, GameState.PlayerList)

    def test_PlayerInitialState(self):
        player = self.player
        
        self.assertEqual(player.coins, 2)
        self.assertTrue(player.alive)        
    
    def test_GiveCards(self):
        """ 
        Test to check if one card or two cards can be given to someone with:
         - two influence
         - one influence
         - no influence
        """
        self.fail("not yet implemented")
    
class BlockingSystem(unittest.TestCase):
    def setUp(self):
        GameState.PlayerList = []
        self.player = Player()
        
    def tearDown(self):
        GameState.reset()
        
    class AlwaysBlockingPlayer(Player):
        def __init__(self, CardUsedToBlock):
            self.CardUsedToBlock = CardUsedToBlock
            Player.__init__(self)
            
        def confirmBlock(self, action): 
            return self.CardUsedToBlock

    class NeverBlockingPlayer(Player):
        def confirmBlock(self, action): return None

    class AlwaysCallingPlayer(Player):
        def confirmCall(self, activePlayer, action): return True
        

    def test_SelfBlocking(self):
        """ Make sure that player can't block themselves """
        player = BlockingSystem.AlwaysBlockingPlayer(action.ForeignAid)
        
        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertNotEqual(player.coins, 2)
    
    def test_ValidBlockAction(self):
        """ Only actions that can block active player's action can be used. This test check that. """
        self.fail("not yet implemented")
    
    def test_BlockingAction(self):
        """ Test if players can block """
        #todo: use a mock object to create a mock action that is blockable
        
        player            = self.player
        player_blocker    = BlockingSystem.AlwaysBlockingPlayer(action.ForeignAid)
        
        self.assertIn(player_blocker, GameState.PlayerList)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertEqual(player.coins, 2)
        
        self.assertFalse(status, response)
        expectedMessage = "Blocked by %s" % player_blocker.name
        self.assertEqual(response, expectedMessage)

    def test_BlockingAction_NoResponse(self):
        """ Test if players can block """
        #todo: use a mock object to create a mock action that is blockable
        player            = self.player
        player_nonblocker = BlockingSystem.NeverBlockingPlayer()
        
        self.assertIn(player_nonblocker, GameState.PlayerList)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)        
        print(status,response)
        self.assertEqual(player.coins, 4)
        
        self.assertTrue(status)
    
    def test_CallBlockingActionAsBluff_Success(self):
        """ 
        Opoosing player blocks action. 
        Active player calls bluff. 
        Opposing player is bluffing and should lose influence.
        The active player's action should succeed.
        """
        #todo: use a mock object to create a mock action that is blockable
        
        player            = BlockingSystem.AlwaysCallingPlayer()
        player_blocker    = BlockingSystem.AlwaysBlockingPlayer(action.Duke)
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
        #todo: use a mock object to create a mock action that is blockable
        
        player            = BlockingSystem.AlwaysCallingPlayer()
        player_blocker    = BlockingSystem.AlwaysBlockingPlayer(action.Duke)
        player_blocker.influence = [action.Duke, action.Duke]
        
        self.assertEqual(len(player.influence), 2)
        self.assertEqual(len(player_blocker.influence), 2)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertFalse(status)
        self.assertEqual(player.coins, 2)
        
        self.assertEqual(len(player.influence), 1)
        self.assertEqual(len(player_blocker.influence), 2)
        

    
class ActionBlocking(unittest.TestCase):
    def setUp(self):
        GameState.PlayerList = []
        self.player = Player()
        
    def tearDown(self):
        GameState.reset()
        
    class AlwaysBlockingPlayer(Player):
        def confirmBlock(self, action): return True

    class NeverBlockingPlayer(Player):
        def confirmBlock(self, action): return None

    class AlwaysCallingPlayer(Player):
        def confirmCall(self, activePlayer, action): return True

    def test_ForeignAid(self):
        """ Test for players blocking foriegn aid """
        #todo: use a mock object to create a mock action that is blockable
        player            = self.player
        player_blocker    = ActionBlocking.AlwaysBlockingPlayer()
        
        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertFalse(status, response)                
        self.assertEqual(player.coins, 2)
        
    # todo: add tests for all cards

class CallBluff(unittest.TestCase):
    def setUp(self):
        GameState.PlayerList = []
        self.player = Player()
        
    def tearDown(self):
        GameState.reset()

    class AlwaysCallingPlayer(Player):
        def confirmCall(self, activePlayer, action): return True

    class AlwaysBlockingPlayer(Player):
        def confirmBlock(self, action): return True

    def test_SelfCalling(self):
        """ Make sure that player can't call themselves as bluffers"""
        class GenericCardThatCanBlockItself(action.Action):
            name = "Generic Card That Can Block Itelf"
            description = "For testing purposes"
            
            def play(self, player, target = None):
                player.coins += 1
                return True, "Success"

        player = CallBluff.AlwaysBlockingPlayer()
        
        self.assertEqual(player.coins, 2)
        status, response = player.play(GenericCardThatCanBlockItself)
        self.assertEqual(player.coins, 3)
    
    def test_CallActivePlayerBluff_Success(self):
        """ Test if other players can call active player's bluff """
        player = self.player
        player.giveCards(action.Income)      #todo: add mock object for action
        self.assertEqual(len(player.influence), 2)
        
        player_CallBluff = CallBluff.AlwaysCallingPlayer()
        
        playedAction = action.ForeignAid
        self.assertEqual(player.coins, 2)
        status, response = player.play(playedAction)
        self.assertEqual(player.coins, 2)

        self.assertEqual(len(player.influence), 1)
        self.assertFalse(status, response)                
        expectedMessage = "Bluffing %s failed for %s" % (playedAction.name, player)
        self.assertEqual(response, expectedMessage)

    def test_CallActivePlayerBluff_Failed(self):
        """ Test if other players can call active player's bluff """
        player = self.player
        player.giveCards(action.ForeignAid)
        self.assertEqual(len(player.influence), 2)
        
        player_CallBluff = CallBluff.AlwaysCallingPlayer()
        
        playedAction = action.ForeignAid
        self.assertEqual(player.coins, 2)
        status, response = player.play(playedAction)
        self.assertEqual(player.coins, 4)

        self.assertEqual(len(player.influence), 2)
        self.assertTrue(status)
        
if __name__ == "__main__":
    unittest.main()