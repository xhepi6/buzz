from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class SpyfallRole(str, Enum):
    SPY = "spy"
    REGULAR = "regular"

class SpyfallRoleInfo(BaseModel):
    role: SpyfallRole
    location: Optional[str] = None
    description: str

    class Config:
        use_enum_values = True

class SpyfallPlayer(BaseModel):
    user_id: str
    nickname: str
    role_info: Optional[SpyfallRoleInfo] = None

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if data.get('role_info') and data['role_info'].get('role'):
            if hasattr(data['role_info']['role'], 'value'):
                data['role_info']['role'] = data['role_info']['role'].value
        return data

# Default locations list
DEFAULT_LOCATIONS = [
    "Airplane",
    "Bank",
    "Beach",
    "Hospital",
    "Hotel",
    "Military Base",
    "Movie Studio",
    "Ocean Liner",
    "Passenger Train",
    "Pirate Ship",
    "Police Station",
    "Restaurant",
    "School",
    "Space Station",
    "Submarine",
    "Supermarket",
    "Theater",
    "University",
    "Casino",
    "Circus"
]

class SpyfallGame(BaseModel):
    players: List[SpyfallPlayer]
    location: str
    round_end_time: str  # ISO format timestamp
    custom_locations: List[str] = [] 