from action import *
import random

class Player():
    def __init__(self):
        self.coins = 2
        self.alive = True
        self.influence = [Action, Action]

    def play(self, action, target = None):
        return action.play(action, self, target)
    
    def loseInfluence(self):
        loses = random.choice(self.influence)  # todo: change from random choice to player choice
    
        self.influence.remove(loses)
        if not len(self.influence):
            self.alive = False            