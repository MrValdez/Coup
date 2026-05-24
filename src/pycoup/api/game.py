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
        self.next_player_id = 0
        self.game = game
        self.players = {}
        self.has_started = False

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
        if next_player_id := self.cache.get_room(self.id, "next_player_id"):
            self.next_player_id = next_player_id

    def add_or_update_player(self, player_id: str, name: str):
        self.load()
        if player_id not in self.players:
            self.players[player_id] = {}

        player = self.players[player_id]
        player["slot_id"] = self.next_player_id
        player["name"] = name
        self.next_player_id += 1

        self.cache.set_room(self.id, "players", self.players)
        self.cache.set_room(self.id, "next_player_id", self.next_player_id)

    def get_state(self, player_id=None, minimal=False):
        """
        Returns information on the room as a dictionary. If minimal is True, only those with * are returned:
            - *Players
            - Current Turn
            - Current Game State

        If player_id is provided, also return information specific for that player, if they are in cache.
        """
        data = {
            "players": self.players.values(),
            "has_started": self.has_started,
        }
        if not minimal:
            data.update({})
        if player_id and player_id in self.players:
            data.update({
                "your_index": self.players[player_id]["slot_id"],
            })

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

    def create_room(self):
        room = Room(self)
        self.add_room_id(room.id)
        return room

    def get_rooms(self, minimal=True):
        room_ids = self.get_room_ids()
        rooms = {}

        for id in room_ids:
            key = f"{id}:{ROOM_HEADER}"
            room = Room(self, id)
            rooms[id] = room.get_state(minimal=minimal)

        return rooms

    def get_room(self, id):
        if id not in self.get_room_ids():
            return None

        return Room(self, id)

    def get_room_state(self, id, player_id=None):
        """ if player_id is given, we can include data specific to player """
        room = self.get_room(id)
        if room is None:
            return None

        return room.get_state(player_id, minimal=False)


if __name__ == "__main__":
    from . import utils

    game = Game()

    #a = Room(game)
    a = game.create_room()

    for i in range(3):
        id = game.generate_player_id()
        name = utils.generate_random_name()
        a.add_or_update_player(id, name)

    a.load()
    print(a.get_state())
    print(game.get_room_ids())
