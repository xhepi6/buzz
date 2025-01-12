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
    game_config: Dict[str, Any]

    def validate_mafia_config(self):
        if self.game_type == "mafia":
            if not isinstance(self.game_config.get("roles"), dict):
                raise ValueError("Mafia game requires roles configuration")
            
            roles = self.game_config["roles"]
            total_players = (
                roles.get("mafia", 0) +
                roles.get("civilian", 0) +
                roles.get("doctor", 0) +
                roles.get("police", 0)
            )
            
            # Validate minimum players
            if total_players < 4:
                raise ValueError("Mafia game requires at least 4 players")
            
            # Validate role distribution
            if roles.get("mafia", 0) < 1:
                raise ValueError("At least 1 mafia required")
            if roles.get("civilian", 0) < 2:
                raise ValueError("At least 2 civilians required")
            
            # Validate special roles for small games
            if total_players <= 5:
                if roles.get("doctor", 0) > 0 or roles.get("police", 0) > 0:
                    raise ValueError("Special roles not recommended for games with 5 or fewer players")
