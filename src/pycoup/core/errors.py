# Coup specific exceptions
#   TargetRequiredError
#   NotEnoughCoinsError
#   BlockOnlyError
#   DeadPlayerError
#   InvalidTargetError
#   ActionNotAllowedError
#   MajorError
class TargetRequiredError(Exception):
    pass


class BlockOnlyError(Exception):
    pass


class DeadPlayerError(Exception):
    pass


class NotEnoughCoinsError(Exception):
    def __init__(self, coins_needed: int):
        self.coins_needed = coins_needed


class InvalidTargetError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class ActionNotAllowedError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class MajorError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message
