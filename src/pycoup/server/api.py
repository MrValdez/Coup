from fastapi import FastAPI
from src.pycoup.api.game import Game, Room

fastapi = FastAPI()


@fastapi.get("/room/list")
def room_list():
    game = Game()
    rooms = game.get_rooms()

    return rooms


@fastapi.get("/room/{id}")
def get_room_state(id):
    game = Game()
    state = game.get_room_state(id)

    return state
