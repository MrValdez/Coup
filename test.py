import unittest
import action
from player import Player

class Actions(unittest.TestCase):
    def setUp(self):
        self.player = Player()
        self.assertEqual(self.player.coins, 2)

    def test_Income(self):
        player = self.player
        
        player.play(action.Income)
        self.assertEqual(player.coins, 3)
            
    def test_ForeignAid(self):
        player = self.player
        
        player.play(action.ForeignAid)
        self.assertEqual(player.coins, 4)
    
if __name__ == "__main__":
    unittest.main()