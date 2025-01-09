from typing import Annotated
from bson.objectid import ObjectId
from pydantic import BaseModel, Field, BeforeValidator

# Custom type for converting string to ObjectId and back
ObjectIdStr = Annotated[str, BeforeValidator(lambda x: str(x) if isinstance(x, ObjectId) else x)]

class GameBase(BaseModel):
    name: str
    description: str
    thumbnail_url: str
    image_url: str
    slug: str
    category: str
    min_players: int
    max_players: int
    duration_minutes: int

class Game(GameBase):
    id: ObjectIdStr = Field(alias="_id", default=None)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Mafia",
                "description": "A social deduction game",
                "thumbnail_url": "/images/mafia-thumb.webp",
                "image_url": "/images/mafia.webp",
                "category": "social-deduction",
                "min_players": 6,
                "max_players": 12,
                "duration_minutes": 30
            }
        }
    }