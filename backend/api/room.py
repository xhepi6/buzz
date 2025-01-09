from fastapi import APIRouter, HTTPException, Depends
from models.room import Room, RoomCreate
from services.room_service import RoomService
from api.auth import get_current_user
from models.user import User

router = APIRouter()

@router.post("/rooms", response_model=Room)
async def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        return await RoomService.create_room(room_data, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/rooms/{room_id}", response_model=Room)
async def get_room(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    room = await RoomService.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room
    