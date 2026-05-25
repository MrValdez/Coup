from fastapi import FastAPI, WebSocket
from air.requests import Request
from src.pycoup.api.game import Game, Room

fastapi = FastAPI()


def get_player_id(request: Request):
    game = Game()
    if "player-hash-id" not in request.session:
        request.session["player-hash-id"] = game.generate_player_id()

    return request.session["player-hash-id"]


@fastapi.get("/room/list")
async def room_list():
    game = Game()
    rooms = game.get_rooms()

    return rooms


@fastapi.get("/room/{id}")
async def get_room_state(id, player_id=None):
    game = Game()
    state = game.get_room_state(id, player_id)

    return state

from fastapi import WebSocket
from dataclasses import dataclass

@dataclass
class RoomData:
    websocket: WebSocket
    player_id: str

class ChatManager:
    def __init__(self):
        self.rooms: Dict[str, List[RoomData]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, player_id: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        data = RoomData(websocket=websocket, player_id=player_id)
        self.rooms[room_id].append(data)

    async def disconnect(self, websocket: WebSocket, room_id: str, player_id: str):
        if room_id not in self.rooms:
            return

        to_delete = None
        for room in self.rooms[room_id]:
            if room.websocket == websocket and room.player_id == player_id:
                to_delete = room
                break
        if to_delete:
            self.rooms[room_id].remove(to_delete)

        if not self.rooms[room_id]:
            # no more clients in room
            del self.rooms[room_id]

    async def broadcast(self, room_id: str, player_id: str, msg: str):
        if room_id not in self.rooms:
            return

        game = Game()
        room = game.get_room(room_id)
        player_name = room.get_player_name(player_id)
        msg = f"{player_name}: {msg}"

        for data in self.rooms[room_id]:
            await data.websocket.send_text(msg)

chat_manager = ChatManager()

@fastapi.websocket("/chat/{room_id}")
async def chat_ws(websocket: WebSocket, room_id: str):
    player_id = websocket.query_params.get("player_id")
    # todo: player_id should be part of auth

    await chat_manager.connect(websocket, room_id, player_id)
    try:
        while True:
            msg = await websocket.receive_text()
            await chat_manager.broadcast(room_id, player_id, msg)
    except:
        await chat_manager.disconnect(websocket, room_id, player_id)
