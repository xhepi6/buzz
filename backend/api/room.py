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
        room = await RoomService.start_game(room_code, current_user)
        
        # Get the game state which contains player roles
        game_state = room.game_state
        if not game_state or 'players' not in game_state:
            raise ValueError("Game state not properly initialized")
            
        # Create a mapping of user_id to their role info
        role_mapping = {
            player['user_id']: player['role_info']
            for player in game_state['players']
        }
        
        # Broadcast game started event to all players
        await manager.broadcast_to_lobby(room_code, {
            "type": "game_started",
            "game_type": room.game_type,
            "room_code": room.code
        })
        
        # For each player, send their role from the game state
        for player in room.players:
            role_info = role_mapping.get(player.user_id)
            if not role_info:
                print(f"⚠️ No role info found for player {player.nickname}")
                continue
                
            print(f"👤 Sending role to player {player.nickname}: {role_info}")
            await manager.send_to_user(
                room_code,
                str(player.user_id),
                {
                    "type": "game_update",
                    "event": "role_assigned",
                    "player_id": str(player.user_id),
                    "role_info": role_info
                }
            )
            
        return room
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Error in start_game endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/lobby/{room_id}")
async def lobby_websocket_endpoint(websocket: WebSocket, room_id: str):
    print(f"🏠 Lobby WebSocket connection attempt for room: {room_id}")
    try:
        await websocket.accept()
        print(f"✅ Lobby WebSocket connection accepted for room: {room_id}")
        
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
            print(f"👤 Lobby WebSocket authenticated for user: {user.nickname}")
        except Exception as e:
            print(f"❌ Token validation error: {e}")
            await websocket.close(code=4002)
            return

        # Get room to validate it exists
        room = await RoomService.get_room(room_id)
        if not room:
            print(f"❌ Room {room_id} not found")
            await websocket.close(code=4004)
            return
            
        # Add to manager's lobby connections
        await manager.connect_to_lobby(websocket, room_id)
        print(f"🔗 WebSocket added to lobby manager: {room_id}")
        
        # Send initial room state
        await websocket.send_json({
            "type": "room_update",
            "room": room.model_dump(),
            "timestamp": datetime.now().isoformat(),
            "players": [
                {
                    "user_id": p.user_id,
                    "nickname": p.nickname,
                    "state": p.state,
                    "is_host": p.user_id == room.host
                }
                for p in room.players
            ]
        })
        
        try:
            while True:
                data = await websocket.receive_text()
                # Handle lobby-specific messages here if needed
                print(f"📥 Received lobby message: {data}")
                
        except WebSocketDisconnect:
            print(f"🔌 Lobby WebSocket disconnected for room: {room_id}")
            manager.disconnect_from_lobby(websocket, room_id)
            
    except Exception as e:
        print(f"❌ Lobby WebSocket error: {e}")
        try:
            manager.disconnect_from_lobby(websocket, room_id)
            await websocket.close()
        except:
            pass

@router.websocket("/ws/game/{room_id}")
async def game_websocket_endpoint(websocket: WebSocket, room_id: str):
    print(f"🎮 Game WebSocket connection attempt for room: {room_id}")
    try:
        await websocket.accept()
        print(f"✅ Game WebSocket connection accepted for room: {room_id}")
        
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
            print(f"👤 Game WebSocket authenticated for user: {user.nickname}")
        except Exception as e:
            print(f"❌ Token validation error: {e}")
            await websocket.close(code=4002)
            return

        # Get room and validate game is in progress
        room = await RoomService.get_room(room_id)
        if not room or room.room_state != "in_game":
            print(f"❌ Room {room_id} not found or not in game state")
            await websocket.close(code=4004)
            return
            
        # Add to manager's game connections
        manager.game_connections[room_id].add(websocket)
        print(f"🔗 WebSocket added to game manager: {room_id}")
        
        # Send initial game state
        game_state = room.game_state
        if game_state:
            player_state = next(
                (p for p in game_state['players'] if p['user_id'] == str(user.id)), 
                None
            )
            if player_state:
                await websocket.send_json({
                    "type": "game_update",
                    "event": "role_assigned",
                    "player_id": str(user.id),
                    "role_info": player_state['role_info']
                })
        
        try:
            while True:
                data = await websocket.receive_json()
                # Handle game-specific messages here
                print(f"📥 Received game message: {data}")
                
        except WebSocketDisconnect:
            print(f"🔌 Game WebSocket disconnected for room: {room_id}")
            manager.game_connections[room_id].discard(websocket)
            
    except Exception as e:
        print(f"❌ Game WebSocket error: {e}")
        try:
            manager.game_connections[room_id].discard(websocket)
            await websocket.close()
        except:
            pass

@router.post("/rooms/{room_code}/restart", response_model=Room)
async def restart_game(
    room_code: str,
    current_user: User = Depends(get_current_user)
):
    try:
        print(f"🔄 Attempting to restart game for room: {room_code}")
        room = await RoomService.restart_game(room_code, current_user)
        
        # Broadcast game restart event to all players
        await manager.broadcast_to_game(room_code, {
            "type": "game_ended",
            "event": "restart",
            "room_code": room.code
        })
        
        # Broadcast room update to lobby
        await manager.broadcast_to_lobby(room_code, {
            "type": "room_update",
            "room": room.model_dump(),
            "timestamp": datetime.now().isoformat(),
            "players": [
                {
                    "user_id": p.user_id,
                    "nickname": p.nickname,
                    "state": p.state,
                    "is_host": p.user_id == room.host
                }
                for p in room.players
            ]
        })
            
        return room
    except ValueError as e:
        print(f"❌ Validation error in restart_game: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Error in restart_game endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
