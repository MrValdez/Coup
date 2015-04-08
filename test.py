import unittest
import action
from player import Player

class Actions(unittest.TestCase):
    def setUp(self):
        self.player = Player()
        self.assertEqual(self.player.coins, 2)
        self.assertTrue(self.player.alive)

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
                
if __name__ == "__main__":
    unittest.main()