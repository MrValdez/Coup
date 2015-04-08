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
    
class ActionBlocks(unittest.TestCase):
    def setUp(self):
        GameState.PlayerList = []
        self.player = Player()
        
    def tearDown(self):
        GameState.reset()
        
    class AlwaysBlockingPlayer(Player):
        def confirmBlock(self, action): return True

    class NeverBlockingPlayer(Player):
        def confirmBlock(self, action): return False
            
    def test_SelfBlocking(self):
        """ Make sure that player can't block themselves """
        player            = ActionBlocks.AlwaysBlockingPlayer()
        
        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertNotEqual(player.coins, 2)
            
    def test_BlockingAction(self):
        """ Test if players can block """
        #todo: use a mock object to create a mock action that is blockable
        
        player            = self.player
        player_blocker    = ActionBlocks.AlwaysBlockingPlayer()
        
        self.assertIn(player_blocker, GameState.PlayerList)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertEqual(player.coins, 2)
        
        self.assertFalse(status, response)
        expectedMessage = "Blocked by %s" % player_blocker
        self.assertEqual(response, expectedMessage)

    def test_BlockingAction_NoResponse(self):
        """ Test if players can block """
        #todo: use a mock object to create a mock action that is blockable
        player            = self.player
        player_nonblocker = ActionBlocks.NeverBlockingPlayer()
        
        self.assertIn(player_nonblocker, GameState.PlayerList)

        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)        
        self.assertEqual(player.coins, 4)
        
        self.assertTrue(status)
    
    def test_ForeignAid(self):
        """ Test for players blocking foriegn aid """
        #todo: use a mock object to create a mock action that is blockable
        player            = self.player
        player_blocker    = ActionBlocks.AlwaysBlockingPlayer()
        
        self.assertEqual(player.coins, 2)
        status, response = player.play(action.ForeignAid)
        self.assertFalse(status, response)                
        self.assertEqual(player.coins, 2)

class CallBluff(unittest.TestCase):
    def setUp(self):
        GameState.PlayerList = []
        self.player = Player()
        
    def tearDown(self):
        GameState.reset()

    class AlwaysCallingPlayer(Player):
        def confirmCall(self, action): return True
    
    def test_CallActivePlayerBluff_Success(self):
        """ Test if other players can call active player's bluff """
        player           = self.player
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
        player           = self.player
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