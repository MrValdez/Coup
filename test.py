import unittest
import action
from player import Player

class Actions(unittest.TestCase):
    def test_IncomeAction(self):
        player = Player()
        
        #print("Income is ", player.coins)
        
        self.assertEqual(player.coins, 2)
        player.play(action.Income)
        self.assertEqual(player.coins, 3)
        
        #print("Income is now ", player.coins)
    
if __name__ == "__main__":
    unittest.main()