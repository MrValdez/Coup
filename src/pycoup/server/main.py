import air
from fastapi import status
import os

from time import time
from pathlib import Path
from air.requests import Request
from . import api, models

from src.pycoup.api.game import Game
from src.pycoup.api import utils


current_directory = Path(__file__).resolve().parent

app = air.Air()
app.add_middleware(air.SessionMiddleware, secret_key=os.environ.get("secret-key", "unsecured-ABCD"))

jinja = air.JinjaRenderer(current_directory / "templates")


@app.post("/api/player")
async def change_player_name_form(request: Request):
    form = await models.PlayerForm.from_request(request)

    # todo: Air csrf is not yet implemented as of this time. For now, let's skip errors
    #if form.is_valid:
    #    set_display_name(request, form)
    #return await lobby(request, extra_data={"error": air.Raw(str(form.errors))})

    set_display_name(request, form.submitted_data.get("name"))

    # Force the browser to use GET for the next request
    status_code = status.HTTP_303_SEE_OTHER
    return air.RedirectResponse(url=app.url_path_for("lobby"), status_code=status_code)

def set_display_name(request: Request, name):
    player_id = get_player_id(request)
    request.session["player-display-name"] = name
    game = Game()
    #game.addPlayer


def get_display_name(request: Request) -> str:
    name = request.session.get("player-display-name")
    if not name:
        name = utils.generate_random_name()
        set_display_name(request, name)
    return name


def get_user_data(request: Request) -> dict:
    player_id = get_player_id(request)
    display_name = get_display_name(request)

    return {
        "player_id": player_id,
        "display_name": display_name,
        "display_name_html": air.Form(
                air.Fieldset(
                    air.Div(
                        air.Label("Your name:"),
                        air.Em("If blank, a random name will be provided"),
                    ),
                    air.Input(name="name", value=display_name),
                    air.Input(type="Submit", value="change name"),
                    class_="grid",
                ),
                method="POST",
                action=app.url_path_for("change_player_name_form"),
                class_="player_name",
            ),
    }

from typing import Optional

@app.get("/")
async def lobby(request: Request, extra_data: Optional[dict[str, str]] = {}):
    content = get_rooms(request)

    return jinja(
        request,
        "base.html",
        title="pyCoup",
        content=content,
        **get_user_data(request),
        **extra_data,
    )


def get_rooms(request):
    rows = []
    rooms = api.room_list()
    for id, room in rooms.items():
        players = ", ".join(room["players"])

        room_url = app.url_path_for("room", id=id)
        join_button = air.Button("Join", onclick=f"location.href='{room_url}'")

        rows.append(
            air.Tr(air.Td(id), air.Td(players), air.Td(join_button))
        )

    content = (
        air.Table(
            air.Tr(
                air.Th("Room Id"), air.Th("Players"),
            ),
            *rows
        )
    )

    return content


@app.get("/room/{id}")
async def room(id: str, request: Request):
    content = api.get_room_state(id)
    if content:
        title = f"pyCoup Room #{id}"
    else:
        content = air.A("Return to lobby", href=app.url_path_for("lobby"))
        title = f"pyCoup Room not found"

    return jinja(
        request,
        "base.html",
        title=title,
        content=content,
        **get_user_data(request),
    )


@app.get("/api/player/id")
def get_player_id(request: Request):
    game = Game()
    if "player-hash-id" not in request.session:
        request.session["player-hash-id"] = game.generate_player_id()

    return request.session["player-hash-id"]


app.mount("/api", api.fastapi)
