from typing import List, Dict, Union, Literal
from datetime import datetime
from pydantic import BaseModel, BeforeValidator, Field
from bson.objectid import ObjectId
from typing import Annotated

# Custom type for ObjectId
ObjectIdStr = Annotated[str, BeforeValidator(lambda x: str(x) if isinstance(x, ObjectId) else x)]

class PlayerState(BaseModel):
    user_id: str
    state: Literal["ready", "not_ready"] = "not_ready"

class ChatMessage(BaseModel):
    user_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MafiaConfig(BaseModel):
    roles: Dict[str, int]  # e.g., {"mafia": 2, "civilian": 4, "doctor": 1}
    moderator: bool = False

class SpyfallConfig(BaseModel):
    round_minutes: int
    spy_count: int
    use_custom_locations: bool = False
    custom_locations: List[str] = []

class RoomCreate(BaseModel):
    game_type: Literal["mafia", "spyfall"]
    num_players: int
    game_config: Union[MafiaConfig, SpyfallConfig]

class Room(BaseModel):
    id: ObjectIdStr = Field(alias="_id", default=None)
    game_type: Literal["mafia", "spyfall"]
    room_state: Literal["lobby", "in_game"] = "lobby"
    num_players: int
    players: List[PlayerState] = []
    game_config: Union[MafiaConfig, SpyfallConfig]
    host: str
    chat_history: List[ChatMessage] = []
    can_start: bool = False

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "game_type": "mafia",
                "room_state": "lobby",
                "num_players": 6,
                "players": [{"user_id": "user123", "state": "ready"}],
                "game_config": {"roles": {"mafia": 2, "civilian": 3, "doctor": 1}, "moderator": True},
                "host": "user123",
                "chat_history": [],
                "can_start": False,
            }
        }
