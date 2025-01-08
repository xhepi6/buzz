from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4

class GameBase(BaseModel):
    name: str
    description: str
    thumbnail_url: str
    image_url: str
    category: str
    min_players: int
    max_players: int
    duration_minutes: int


class Game(GameBase):
    id: UUID = Field(default_factory=uuid4)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Mafia",
                "description": "A social deduction game where innocent villagers try to identify the mafia among them.",
                "thumbnail_url": "/static/images/games/mafia-thumbnail.webp",
                "image_url": "/static/images/games/mafia.webp",
                "category": "social-deduction",
                "min_players": 6,
                "max_players": 12,
                "duration_minutes": 30
            }
        }
