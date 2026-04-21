# Coup specific exceptions
#   TargetRequired
#   NotEnoughCoins
#   BlockOnly
#   DeadPlayer
#   InvalidTarget
#   ActionNotAllowed
#   MajorError
class TargetRequired(Exception):
    pass


class BlockOnly(Exception):
    pass


class DeadPlayer(Exception):
    pass


class NotEnoughCoins(Exception):
    def __init__(self, coins_needed: int):
        self.coins_needed = coins_needed


class InvalidTarget(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class ActionNotAllowed(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class MajorError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message
