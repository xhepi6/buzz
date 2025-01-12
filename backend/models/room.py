from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, BeforeValidator
from typing_extensions import Annotated
from bson.objectid import ObjectId
import random


PyObjectId = Annotated[str, BeforeValidator(lambda x: str(x))]

class PlayerState(BaseModel):
    user_id: str
    nickname: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    state: str = "not_ready"

class Room(BaseModel):
    id: PyObjectId = Field(alias="_id")
    code: str  # 4-digit room code
    game_type: str
    room_state: str
    num_players: int
    players: List[PlayerState]
    game_config: Dict[str, Any]
    host: str
    chat_history: List[Dict[str, Any]]
    can_start: bool

    class Config:
        populate_by_name = True

class MafiaRoles(BaseModel):
    mafia: int
    civilian: int
    doctor: Optional[int] = 0
    police: Optional[int] = 0
    moderator: bool = False

class MafiaConfig(BaseModel):
    roles: MafiaRoles
    moderator: bool = False

class RoomCreate(BaseModel):
    game_type: str
    num_players: int
    game_config: Dict[str, Any]  # Keep this flexible for different game types

    def validate_mafia_config(self):
        if self.game_type == "mafia":
            if not isinstance(self.game_config.get("roles"), dict):
                raise ValueError("Mafia game requires roles configuration")
            # Add more validation as needed
