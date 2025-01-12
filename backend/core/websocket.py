from typing import Dict, Set
from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        # room_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        
    async def connect(self, websocket: WebSocket, room_id: str):
        # Don't accept the connection here, just add it to the set
        self.active_connections[room_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        self.active_connections[room_id].discard(websocket)
        # Clean up empty rooms
        if not self.active_connections[room_id]:
            del self.active_connections[room_id]
    
    async def broadcast_to_room(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection, room_id)

    async def send_to_user(self, room_id: str, user_id: str, message: dict):
        """Send a message to a specific user in a room"""
        if room_id in self.active_connections:
            for websocket in self.active_connections[room_id]:
                try:
                    # Check if this connection belongs to the target user
                    if getattr(websocket, "user_id", None) == user_id:
                        await websocket.send_json(message)
                except Exception as e:
                    print(f"Error sending to user {user_id}: {e}")

# Global instance
manager = ConnectionManager() 
