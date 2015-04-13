# Coup specific exceptions
#   TargetRequired
#   NotEnoughCoins
#   BlockOnly
#   DeadPlayer
#   InvalidTarget
#   ActionNotAllowed
#   MajorError
class TargetRequired(Exception):   pass
class BlockOnly(Exception):        pass
class DeadPlayer(Exception):       pass

class NotEnoughCoins(Exception):
    def __init__(self, coinsNeeded):
        self.coinsNeeded = coinsNeeded
        
class InvalidTarget(Exception):    
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class ActionNotAllowed(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class MajorError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message
