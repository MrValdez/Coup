import main

def testIncomeAction():
    player = main.Player()
    
    print("Income is ", player.coins)
    player.play(main.Income)
    print("Income is now ", player.coins)
    
testIncomeAction()