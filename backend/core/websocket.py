from typing import Dict, Set
from fastapi import WebSocket
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # room_id -> set of WebSocket connections
        self.lobby_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.game_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        
    async def connect_to_lobby(self, websocket: WebSocket, room_id: str):
        if room_id not in self.lobby_connections:
            self.lobby_connections[room_id] = set()
        self.lobby_connections[room_id].add(websocket)
        logger.debug("Added connection to lobby %s", room_id)
    
    async def connect_to_game(self, websocket: WebSocket, room_id: str):
        if room_id not in self.game_connections:
            self.game_connections[room_id] = set()
        self.game_connections[room_id].add(websocket)
        logger.debug("Added connection to game %s", room_id)
    
    def disconnect_from_lobby(self, websocket: WebSocket, room_id: str):
        if room_id in self.lobby_connections:
            self.lobby_connections[room_id].discard(websocket)
            logger.debug("Removed connection from lobby %s", room_id)
    
    def disconnect_from_game(self, websocket: WebSocket, room_id: str):
        if room_id in self.game_connections:
            self.game_connections[room_id].discard(websocket)
            logger.debug("Removed connection from game %s", room_id)
    
    async def broadcast_to_lobby(self, room_id: str, message: dict):
        if room_id in self.lobby_connections:
            disconnected = set()
            for connection in self.lobby_connections[room_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error("Error broadcasting to lobby: %s", str(e))
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect_from_lobby(connection, room_id)

    async def broadcast_to_game(self, room_id: str, message: dict):
        if room_id in self.game_connections:
            disconnected = set()
            for connection in self.game_connections[room_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error("Error broadcasting to game: %s", str(e))
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect_from_game(connection, room_id)

    async def send_to_user(self, room_id: str, user_id: str, message: dict, connection_type: str = 'lobby'):
        """Send a message to a specific user in a room"""
        connections = self.lobby_connections if connection_type == 'lobby' else self.game_connections
        
        if room_id in connections:
            for websocket in connections[room_id]:
                try:
                    # Check if this connection belongs to the target user
                    if getattr(websocket, "user_id", None) == user_id:
                        await websocket.send_json(message)
                        logger.debug("Sent message to user %s in %s", user_id, connection_type)
                        return  # Message sent successfully
                except Exception as e:
                    logger.error("Error sending to user: %s", str(e))
                    connections[room_id].discard(websocket)

        # If we get here, either the room doesn't exist or the user wasn't found
        logger.error("⚠️ Could not send message to user %s in room %s (%s)", user_id, room_id, connection_type)

# Global instance
manager = ConnectionManager() 
