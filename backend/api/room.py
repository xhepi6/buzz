from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from api.auth import get_current_user
from services.game_service import GameService
from models.room import Room, RoomCreate
from services.room_service import RoomService
from models.user import User
from core.websocket import manager
from datetime import datetime
from typing import List, Optional

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
    try:
        print(f"Getting room {room_code} for user {current_user.id}")
        room = await RoomService.get_room(room_code)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room
    except Exception as e:
        print(f"Error getting room: {e}")
        raise

@router.post("/rooms/{room_code}/join", response_model=Room)
async def join_room(
    room_code: str,
    current_user: User = Depends(get_current_user)
):
    try:
        print(f"👤 User {current_user.id} ({current_user.nickname}) attempting to join room {room_code}")
        room = await RoomService.join_room(room_code, current_user)
        print(f"✅ Join successful. Room now has {len(room.players)} players")
        return room
    except ValueError as e:
        print(f"❌ Join failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Error in join_room: {e}")
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

@router.post("/rooms/{room_code}/leave", response_model=Room)
async def leave_room(
    room_code: str,
    current_user: User = Depends(get_current_user)
):
    try:
        return await RoomService.leave_room(room_code, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rooms/{room_code}/start", response_model=Room)
async def start_game(
    room_code: str,
    current_user: User = Depends(get_current_user)
):
    try:
        return await RoomService.start_game(room_code, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    print(f"🔌 WebSocket connection attempt for room: {room_id}")
    try:
        await websocket.accept()
        print(f"✅ WebSocket connection accepted for room: {room_id}")
        
        # Get and validate token
        token = websocket.query_params.get("token")
        if not token:
            print(f"❌ No token provided, closing connection")
            await websocket.close(code=4001)
            return
            
        try:
            user = await get_current_user(token)
            if not user:
                print(f"❌ Invalid token, closing connection")
                await websocket.close(code=4002)
                return
            websocket.user_id = str(user.id)
            print(f"👤 WebSocket authenticated for user: {user.nickname}")
        except Exception as e:
            print(f"❌ Token validation error: {e}")
            await websocket.close(code=4002)
            return

        # Get room first to validate it exists
        room = await RoomService.get_room(room_id)
        if not room:
            print(f"❌ Room {room_id} not found, closing connection")
            await websocket.close(code=4004)
            return
            
        # Add to manager's connections
        manager.active_connections[room_id].add(websocket)
        print(f"🔗 WebSocket added to room manager: {room_id}")
        
        # Send initial state
        initial_data = {
            "type": "room_update",
            "room": room.model_dump(),
            "timestamp": datetime.now().isoformat(),
            "players": [
                {
                    "user_id": player.user_id,
                    "nickname": player.nickname,
                    "state": player.state,
                    "is_host": player.user_id == room.host
                }
                for player in room.players
            ]
        }
        await websocket.send_json(initial_data)
        
        try:
            while True:
                await websocket.receive_text()
                
                # Get and send latest room state
                current_room = await RoomService.get_room(room_id)
                if current_room:
                    await websocket.send_json({
                        "type": "room_update",
                        "room": current_room.model_dump(),
                        "timestamp": datetime.now().isoformat(),
                        "players": [
                            {
                                "user_id": player.user_id,
                                "nickname": player.nickname,
                                "state": player.state,
                                "is_host": player.user_id == current_room.host
                            }
                            for player in current_room.players
                        ]
                    })
                
        except WebSocketDisconnect:
            print(f"🔌 WebSocket disconnected for room: {room_id}")
            manager.disconnect(websocket, room_id)
            
    except Exception as e:
        print(f"❌ WebSocket error in room {room_id}: {e}")
        try:
            manager.disconnect(websocket, room_id)
            await websocket.close()
        except:
            pass
