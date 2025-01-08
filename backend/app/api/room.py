from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from uuid import UUID
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/rooms")
async def create_room(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    # TODO: Implement room creation
    pass

@router.post("/rooms/{room_id}/join")
async def join_room(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    # TODO: Implement room joining
    pass

@router.get("/rooms/{room_id}/state")
async def get_room_state(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    # TODO: Implement getting room state
    pass 