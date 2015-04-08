import unittest
import main

class Actions(unittest.TestCase):
    def test_IncomeAction(self):
        player = main.Player()
        
        #print("Income is ", player.coins)
        
        self.assertEqual(player.coins, 2)
        player.play(main.Income)
        self.assertEqual(player.coins, 3)
        
        #print("Income is now ", player.coins)
    
if __name__ == "__main__":
    unittest.main()