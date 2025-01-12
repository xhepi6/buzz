from enum import Enum
from pydantic import BaseModel
from typing import Optional, List

class SpyfallRole(str, Enum):
    SPY = "spy"
    REGULAR = "regular"

class SpyfallRoleInfo(BaseModel):
    role: SpyfallRole
    location: Optional[str] = None
    location_image: Optional[str] = None
    description: str

class SpyfallPlayer(BaseModel):
    user_id: str
    nickname: str
    role_info: SpyfallRoleInfo 