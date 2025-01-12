from typing import Optional
from bson.objectid import ObjectId
from core.mongodb import mongodb
from models.room import Room, RoomCreate, PlayerState
from models.user import User
import random
import string

class RoomService:
    @staticmethod
    def generate_room_code(length: int = 4) -> str:
        """
        Generate a room code with mix of uppercase letters and numbers.
        Example outputs: 'A2B5', 'X9Y3', 'M4K7'
        """
        # Use only uppercase letters and numbers to avoid confusion
        characters = string.ascii_uppercase + string.digits
        while True:
            # Ensure at least one letter and one number
            code = ''.join(random.choices(characters, k=length))
            if (any(c.isdigit() for c in code) and 
                any(c.isalpha() for c in code)):
                return code

    @staticmethod
    async def create_room(room_data: RoomCreate, user: User) -> Room:
        try:
            # Generate a unique room code
            while True:
                room_code = RoomService.generate_room_code()
                existing_room = await mongodb.db.rooms.find_one({"code": room_code})
                if not existing_room:
                    break

            # Create the host player with user details
            host_player = PlayerState(
                user_id=str(user.id),
                nickname=user.nickname,
                full_name=user.full_name,
                email=user.email,
                state="not_ready"
            )
            
            room_dict = {
                "code": room_code,
                "game_type": room_data.game_type,
                "room_state": "lobby",
                "num_players": room_data.num_players,
                "players": [host_player.model_dump()],
                "game_config": room_data.game_config,
                "host": str(user.id),
                "chat_history": [],
                "can_start": False,
            }
            
            result = await mongodb.db.rooms.insert_one(room_dict)
            if not result.inserted_id:
                raise ValueError("Failed to create room")
            
            created_room = await mongodb.db.rooms.find_one({"_id": result.inserted_id})
            if not created_room:
                raise ValueError("Failed to fetch created room")
            
            created_room["_id"] = str(created_room["_id"])
            
            return Room(**created_room)
        except Exception as e:
            print(f"Error in create_room: {e}")
            raise

    @staticmethod
    async def _enrich_player_data(player_state: dict) -> dict:
        """Helper method to add user details to player state"""
        try:
            # Don't convert to ObjectId, use the UUID string directly
            user = await mongodb.db.users.find_one({"_id": player_state['user_id']})
            if user:
                player_state['nickname'] = user.get('nickname')
                player_state['full_name'] = user.get('full_name')
                player_state['email'] = user.get('email')
            return player_state
        except Exception as e:
            print(f"Error enriching player data: {e}")
            return player_state

    @staticmethod
    async def get_room(room_code: str) -> Optional[Room]:
        try:
            room_doc = await mongodb.db.rooms.find_one({"code": room_code})
            if room_doc:
                # Enrich each player with user data
                enriched_players = []
                for player in room_doc['players']:
                    enriched_player = await RoomService._enrich_player_data(player)
                    enriched_players.append(enriched_player)
                room_doc['players'] = enriched_players
                
                room_doc['_id'] = str(room_doc['_id'])
                return Room(**room_doc)
            return None
        except Exception as e:
            print(f"Error getting room: {e}")
            return None
    
    @staticmethod
    async def join_room(room_code: str, user: User) -> Room:
        # Check if room exists
        room = await RoomService.get_room(room_code)
        if not room:
            raise ValueError("Room not found")
            
        # Check if user is already in the room
        if any(p.user_id == str(user.id) for p in room.players):
            return room
            
        # Check if room is full
        if len(room.players) >= room.num_players:
            raise ValueError("Room is full")
            
        # Add player to room with additional user info
        new_player = PlayerState(
            user_id=str(user.id),
            nickname=user.nickname,
            full_name=user.full_name,
            email=user.email,
            state="not_ready"
        )
        
        result = await mongodb.db.rooms.update_one(
            {"code": room_code},  # Use room code instead of _id
            {"$push": {"players": new_player.model_dump()}}
        )
        
        if result.modified_count == 0:
            raise ValueError("Failed to join room")
            
        return await RoomService.get_room(room_code)

    @staticmethod
    async def toggle_ready(room_code: str, user: User) -> Room:
        # Get current player state
        room = await RoomService.get_room(room_code)
        if not room:
            raise ValueError("Room not found")
        
        player = next((p for p in room.players if p.user_id == str(user.id)), None)
        if not player:
            raise ValueError("User not in room")
        
        # Toggle ready state
        new_state = "not_ready" if player.state == "ready" else "ready"
        
        result = await mongodb.db.rooms.update_one(
            {
                "code": room_code,  # Use room code instead of _id
                "players.user_id": str(user.id)
            },
            {"$set": {"players.$.state": new_state}}
        )
        
        if result.modified_count == 0:
            raise ValueError("Failed to update ready state")
        
        return await RoomService.get_room(room_code)