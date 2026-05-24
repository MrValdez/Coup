import air

from pydantic import BaseModel


class PlayerName(BaseModel):
    name: str


class PlayerForm(air.AirForm):
    model = PlayerName
