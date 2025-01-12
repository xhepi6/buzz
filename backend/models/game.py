from typing import Annotated, Dict, Optional, Any
from bson.objectid import ObjectId
from pydantic import BaseModel, Field, BeforeValidator
from core.config import settings

ObjectIdStr = Annotated[str, BeforeValidator(lambda x: str(x) if isinstance(x, ObjectId) else x)]

def get_full_url(path: str) -> str:
    """Convert a relative path to a full API URL"""
    if path.startswith('http'):
        return path
    return f"{settings.API_URL}{path}"

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
    id: ObjectIdStr = Field(alias="_id")
    name: str
    slug: str
    description: str
    min_players: int
    max_players: int
    category: str
    featured: bool = False
    locations: Optional[Dict[str, str]] = None  # Map location names to their image paths
    settings: Dict[str, Any]

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        # Convert relative paths to full URLs for location images
        if data.get('locations'):
            data['locations'] = {
                name: get_full_url(path)
                for name, path in data['locations'].items()
            }
        return data

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str
        },
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