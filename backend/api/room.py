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
        # Validate mafia config if it's a mafia game
        if room_data.game_type == "mafia":
            room_data.validate_mafia_config()
            
        room = await RoomService.create_room(room_data, current_user)
        if not room:
            raise HTTPException(status_code=500, detail="Failed to create room")
        return room
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error creating room: {e}")  # Add logging
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/rooms/{room_code}", response_model=Room)
async def get_room(
    room_code: str,
    current_user: User = Depends(get_current_user)
):
    room = await RoomService.get_room(room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.post("/rooms/{room_code}/join", response_model=Room)
async def join_room(
    room_code: str,
    current_user: User = Depends(get_current_user)
):
    try:
        return await RoomService.join_room(room_code, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rooms/{room_id}/ready", response_model=Room)
async def toggle_ready(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        return await RoomService.toggle_ready(room_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
