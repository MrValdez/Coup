from shortuuid import uuid
import diskcache


GAME_INFO_ROOMS = "game:rooms"
ROOM_HEADER = "header"


class UnloadedData(Exception):
    pass


class Cache(diskcache.Cache):
    """
    This class will cache information grouped by id
    """

    def __init__(self, directory="cache", *args, **kwargs):
        super().__init__(directory, *args, **kwargs)

    def _update_room_key(self, id, key):
        return f"{id}:{key}"

    def get_room(self, id, key, *args, **kwargs):
        key = self._update_room_key(id, key)
        return super().get(key, *args, **kwargs)

    def set_room(self, id, key, value, *args, **kwargs):
        key = self._update_room_key(id, key)
        return super().set(key, value, *args, **kwargs)


class Room:
    def __init__(self, game, id=None):
        self._id = None
        self.game = game
        self.players = []

        self.cache = game.cache
        if id:
            self.id = id
            self.load()

    @property
    def id(self):
        if self._id is None:
            self._id = uuid()[:5].upper()

        return self._id

    @id.setter
    def id(self, x):
        self._id = x

        self.game.add_room_id(self._id)

    def load(self):
        if players := self.cache.get_room(self.id, "players"):
            self.players = players

    def add_player(self, player):
        self.load()
        self.players.append(player)
        self.cache.set_room(self.id, "players", self.players)

    def get_state(self, minimal=False):
        """
        Returns information on the room as a dictionary. If minimal is True, only those with * are returned:
            - *Players
            - Current Turn
            - Current Game State
        """
        data = {
            "players": self.players,
        }
        if not minimal:
            data.update({})

        return data


class Game:
    def __init__(self, cache_engine=Cache):
        self.cache = cache_engine()

    def generate_player_id(self):
        return uuid()[:5].upper()

    def get_room_ids(self):
        return self.cache.get(GAME_INFO_ROOMS) or set()

    def add_room_id(self, id):
        room_ids = self.get_room_ids()
        room_ids.add(id)
        self.cache.set(GAME_INFO_ROOMS, room_ids)

    def get_rooms(self, minimal=True):
        room_ids = self.get_room_ids()
        rooms = {}

        for id in room_ids:
            key = f"{id}:{ROOM_HEADER}"
            room = Room(self, id)
            rooms[id] = room.get_state(minimal=minimal)

        return rooms

    def get_room_state(self, id):
        if id not in self.get_room_ids():
            return None

        return Room(self, id).get_state(minimal=False)


if __name__ == "__main__":
    defaultNames = ["Leonardo", "Michelangelo", "Raphael", "Donatello", "Splinter", "April"]

    game = Game()
    print(game.get_room_ids())
    print("==")

    a = Room(game)
    for player in defaultNames:
        a.add_player(player)
    id = a.id

    print(id)

    a.add_player("Shredder")
    b = Room(game, id=id)
    print(b.players)

    print(game.get_room_ids())
