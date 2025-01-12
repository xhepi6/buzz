from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class MafiaRole(str, Enum):
    MAFIA = "mafia"
    CIVILIAN = "civilian"
    DOCTOR = "doctor"
    POLICE = "police"

class MafiaRoleInfo(BaseModel):
    role: MafiaRole
    description: str
    teammates: Optional[List[str]] = None

    class Config:
        use_enum_values = True

class MafiaPlayer(BaseModel):
    user_id: str
    nickname: str
    role_info: Optional[MafiaRoleInfo] = None
    is_alive: bool = True
    voted_by: List[str] = []
    protected_by_doctor: bool = False
    investigated_by_police: bool = False

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if data.get('role_info') and data['role_info'].get('role'):
            # Only convert to value if it's an Enum
            if hasattr(data['role_info']['role'], 'value'):
                data['role_info']['role'] = data['role_info']['role'].value
        return data

ROLE_DESCRIPTIONS = {
    MafiaRole.MAFIA: MafiaRoleInfo(
        role=MafiaRole.MAFIA,
        description="You are a member of the Mafia. Work with your fellow mafiosi to eliminate the citizens.",
        teammates=[]
    ),
    MafiaRole.CIVILIAN: MafiaRoleInfo(
        role=MafiaRole.CIVILIAN,
        description="You are a Civilian. Use your wit and observation to identify the Mafia members."
    ),
    MafiaRole.DOCTOR: MafiaRoleInfo(
        role=MafiaRole.DOCTOR,
        description="You are the Doctor. You can save one person each night from being eliminated."
    ),
    MafiaRole.POLICE: MafiaRoleInfo(
        role=MafiaRole.POLICE,
        description="You are the Police Officer. You can investigate one person each night to determine if they are Mafia."
    )
}

class MafiaGame(BaseModel):
    players: List[MafiaPlayer]
    phase: str = "night"  # "night" or "day"
    round: int = 1
    eliminated_players: List[str] = []
    votes: dict = {}
    night_actions: dict = {} 