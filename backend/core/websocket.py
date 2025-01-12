from typing import Dict, Set
from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        # room_id -> set of WebSocket connections
        self.lobby_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.game_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        
    async def connect_to_lobby(self, websocket: WebSocket, room_id: str):
        self.lobby_connections[room_id].add(websocket)
    
    async def connect_to_game(self, websocket: WebSocket, room_id: str):
        self.game_connections[room_id].add(websocket)
    
    def disconnect_from_lobby(self, websocket: WebSocket, room_id: str):
        self.lobby_connections[room_id].discard(websocket)
        if not self.lobby_connections[room_id]:
            del self.lobby_connections[room_id]
            
    def disconnect_from_game(self, websocket: WebSocket, room_id: str):
        self.game_connections[room_id].discard(websocket)
        if not self.game_connections[room_id]:
            del self.game_connections[room_id]
    
    async def broadcast_to_lobby(self, room_id: str, message: dict):
        if room_id in self.lobby_connections:
            disconnected = set()
            for connection in self.lobby_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
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
                except:
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
                        return  # Message sent successfully
                except Exception as e:
                    print(f"Error sending to user {user_id}: {e}")

        # If we get here, either the room doesn't exist or the user wasn't found
        print(f"⚠️ Could not send message to user {user_id} in room {room_id} ({connection_type})")

# Global instance
manager = ConnectionManager() 
