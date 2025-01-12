from typing import Dict, Set
from fastapi import WebSocket
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        
    async def connect(self, websocket: WebSocket, room_id: str):
        if room_id not in self.connections:
            self.connections[room_id] = set()
        self.connections[room_id].add(websocket)
        logger.debug("Added connection to room %s", room_id)
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.connections:
            self.connections[room_id].discard(websocket)
            logger.debug("Removed connection from room %s", room_id)
    
    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.connections:
            disconnected = set()
            for connection in self.connections[room_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error("Error broadcasting: %s", str(e))
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection, room_id)

    async def send_to_user(self, room_id: str, user_id: str, message: dict):
        """Send a message to a specific user in a room"""
        if room_id in self.connections:
            for websocket in self.connections[room_id]:
                try:
                    if getattr(websocket, "user_id", None) == user_id:
                        await websocket.send_json(message)
                        logger.debug("Sent message to user %s", user_id)
                        return
                except Exception as e:
                    logger.error("Error sending to user: %s", str(e))
                    self.connections[room_id].discard(websocket)

        logger.error("⚠️ Could not send message to user %s in room %s", user_id, room_id)

# Global instance
manager = ConnectionManager() 
