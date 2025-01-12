from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from api.auth import get_current_user
from services.game_service import GameService
from models.room import Room, RoomCreate
from services.room_service import RoomService
from models.user import User
from core.websocket import manager
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

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
        logger.info("Room created: %s", room.code)
        return room
    except ValueError as e:
        logger.error("Error creating room: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error creating room: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/rooms/{room_code}", response_model=Room)
async def get_room(
    room_code: str,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info("Getting room %s for user %s", room_code, current_user.id)
        room = await RoomService.get_room(room_code)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room
    except Exception as e:
        logger.error("Error getting room: %s", str(e))
        raise

@router.post("/rooms/{room_code}/join", response_model=Room)
async def join_room(
    room_code: str,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info("👤 User %s (%s) attempting to join room %s", current_user.id, current_user.nickname, room_code)
        room = await RoomService.join_room(room_code, current_user)
        logger.info("✅ Join successful. Room now has %s players", len(room.players))
        return room
    except ValueError as e:
        logger.error("❌ Join failed: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("❌ Error in join_room: %s", str(e))
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
        logger.info("Starting game in room %s", room_code)
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
                logger.warning("⚠️ No role info found for player %s", player.nickname)
                continue
                
            logger.info("👤 Sending role to player %s: %s", player.nickname, role_info)
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
        logger.error("❌ Error in start_game endpoint: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/lobby/{room_id}")
async def lobby_websocket_endpoint(websocket: WebSocket, room_id: str):
    logger.info("Lobby WebSocket connection attempt for room: %s", room_id)
    try:
        await websocket.accept()
        logger.debug("Lobby WebSocket connection accepted for room: %s", room_id)
        
        # Get and validate token
        token = websocket.query_params.get("token")
        if not token:
            logger.warning("No token provided, closing connection")
            await websocket.close(code=4001)
            return
            
        try:
            user = await get_current_user(token)
            if not user:
                logger.warning("Invalid token, closing connection")
                await websocket.close(code=4002)
                return
            websocket.user_id = str(user.id)
            logger.info("Lobby WebSocket authenticated for user: %s", user.nickname)
        except Exception as e:
            logger.error("Token validation error: %s", str(e))
            await websocket.close(code=4002)
            return

        # Get room to validate it exists
        room = await RoomService.get_room(room_id)
        if not room:
            logger.warning("Room %s not found", room_id)
            await websocket.close(code=4004)
            return
            
        # Add to manager's lobby connections
        await manager.connect_to_lobby(websocket, room_id)
        logger.debug("WebSocket added to lobby manager: %s", room_id)
        
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
                logger.debug("Received lobby message: %s", data)
                
        except WebSocketDisconnect:
            logger.info("Lobby WebSocket disconnected for room: %s", room_id)
            manager.disconnect_from_lobby(websocket, room_id)
            
    except Exception as e:
        logger.error("❌ Lobby WebSocket error: %s", str(e))
        try:
            manager.disconnect_from_lobby(websocket, room_id)
            await websocket.close()
        except:
            pass

@router.websocket("/ws/game/{room_id}")
async def game_websocket_endpoint(websocket: WebSocket, room_id: str):
    logger.info("Game WebSocket connection attempt for room: %s", room_id)
    try:
        await websocket.accept()
        logger.debug("Game WebSocket connection accepted for room: %s", room_id)
        
        # Get and validate token
        token = websocket.query_params.get("token")
        if not token:
            logger.warning("No token provided, closing game connection")
            await websocket.close(code=4001)
            return
            
        try:
            user = await get_current_user(token)
            if not user:
                logger.warning("Invalid token, closing game connection")
                await websocket.close(code=4002)
                return
            websocket.user_id = str(user.id)
            logger.info("Game WebSocket authenticated for user: %s", user.nickname)
        except Exception as e:
            logger.error("Token validation error in game connection: %s", str(e))
            await websocket.close(code=4002)
            return

        # Get room to validate it exists
        room = await RoomService.get_room(room_id)
        if not room:
            logger.warning("Room %s not found for game connection", room_id)
            await websocket.close(code=4004)
            return
            
        # Add to manager's game connections
        await manager.connect_to_game(websocket, room_id)
        logger.debug("WebSocket added to game manager: %s", room_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                # Handle game-specific messages here
                logger.debug("Received game message: %s", data)
                
        except WebSocketDisconnect:
            logger.info("Game WebSocket disconnected for room: %s", room_id)
            manager.disconnect_from_game(websocket, room_id)
            
    except Exception as e:
        logger.error("Game WebSocket error: %s", str(e))
        try:
            manager.disconnect_from_game(websocket, room_id)
            await websocket.close()
        except:
            pass

@router.post("/rooms/{room_code}/restart", response_model=Room)
async def restart_game(
    room_code: str,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info("🔄 Attempting to restart game for room: %s", room_code)
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
        logger.error("❌ Validation error in restart_game: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("❌ Error in restart_game endpoint: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
