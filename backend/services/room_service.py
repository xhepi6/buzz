from typing import Optional
from bson.objectid import ObjectId
from core.mongodb import mongodb
from models.room import Room, RoomCreate, PlayerState
from models.user import User

class RoomService:
    @staticmethod
    async def create_room(room_data: RoomCreate, user: User) -> Room:
        host_player = PlayerState(user_id=str(user.id))
        
        room_dict = {
            "game_type": room_data.game_type,
            "room_state": "lobby",
            "num_players": room_data.num_players,
            "players": [host_player.model_dump()],
            "game_config": room_data.game_config.model_dump(),
            "host": str(user.id),
            "chat_history": [],
            "can_start": False,
        }
        
        result = await mongodb.db.rooms.insert_one(room_dict)
        room_dict["_id"] = result.inserted_id
        return Room(**room_dict)

    @staticmethod
    async def get_room(room_id: str) -> Optional[Room]:
        try:
            room_doc = await mongodb.db.rooms.find_one({"_id": ObjectId(room_id)})
            return Room(**room_doc) if room_doc else None
        except Exception as e:
            print(f"Error getting room: {e}")
            return None
    