from typing import Annotated, Optional, Dict, Any
from bson.objectid import ObjectId
from pydantic import BaseModel, Field, BeforeValidator

# Custom type for converting string to ObjectId and back
ObjectIdStr = Annotated[str, BeforeValidator(lambda x: str(x) if isinstance(x, ObjectId) else x)]

class GameBase(BaseModel):
    name: str
    slug: str
    description: str
    thumbnail_url: str
    image_url: str
    category: str
    min_players: int
    max_players: int
    duration_minutes: int
    settings: Dict[str, Any] = {}  # Added settings field

class GameDetails(GameBase):
    """Detailed game model with additional fields for specific game types"""
    rules: dict = {}     # Game-specific rules

class Game(GameBase):
    id: ObjectIdStr = Field(alias="_id", default=None)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Mafia",
                "slug": "mafia",
                "description": "A social deduction game",
                "thumbnail_url": "/images/mafia-thumb.webp",
                "image_url": "/images/mafia.webp",
                "category": "social-deduction",
                "min_players": 3,
                "max_players": 12,
                "duration_minutes": 30,
                "settings": {
                    "roles": {
                        "min_mafia": 1,
                        "max_mafia": 4,
                        "optional_roles": ["doctor", "police", "moderator"]
                    }
                }
            }
        }
    } 