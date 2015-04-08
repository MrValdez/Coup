class Player():
    def __init__(self):
        self.coins = 2

    def play(self, action):
        action.play(action, self)
    