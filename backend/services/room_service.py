from typing import Optional
from bson.objectid import ObjectId
from core.mongodb import mongodb
from models.room import Room, RoomCreate, PlayerState
from models.user import User
import random
import string
from core.websocket import manager
from datetime import datetime

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
        try:
            # Check if room exists
            room = await RoomService.get_room(room_code)
            if not room:
                raise ValueError("Room not found")
            
            # Check if user is already in the room
            if any(p.user_id == str(user.id) for p in room.players):
                print(f"User {user.id} already in room {room_code}")
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
            
            print(f"Adding player to room: {new_player.model_dump()}")
            
            result = await mongodb.db.rooms.update_one(
                {"code": room_code},
                {"$push": {"players": new_player.model_dump()}}
            )
            
            if result.modified_count == 0:
                raise ValueError("Failed to join room")
            
            updated_room = await RoomService.get_room(room_code)
            print(f"Room after join: {updated_room.model_dump()}")
            
            # Broadcast update after successful join
            await manager.broadcast_to_room(
                room_code,
                {
                    "type": "room_update",
                    "event": "player_joined",
                    "room": updated_room.model_dump(),
                    "timestamp": datetime.now().isoformat(),
                    "players": [
                        {
                            "user_id": p.user_id,
                            "nickname": p.nickname,
                            "state": p.state,
                            "is_host": p.user_id == updated_room.host
                        }
                        for p in updated_room.players
                    ],
                    "player": {
                        "user_id": str(user.id),
                        "nickname": user.nickname,
                        "state": "not_ready"
                    }
                }
            )
            return updated_room
            
        except Exception as e:
            print(f"Error in join_room: {e}")
            raise

    @staticmethod
    async def toggle_ready(room_code: str, user: User) -> Room:
        try:
            # Get current player state
            room = await RoomService.get_room(room_code)
            if not room:
                raise ValueError("Room not found")
            
            player = next((p for p in room.players if p.user_id == str(user.id)), None)
            if not player:
                raise ValueError("User not in room")
            
            # Toggle ready state
            new_state = "not_ready" if player.state == "ready" else "ready"
            print(f"🔄 Toggling player {user.nickname} state to: {new_state}")
            
            # Update in database
            result = await mongodb.db.rooms.update_one(
                {
                    "code": room_code,
                    "players.user_id": str(user.id)
                },
                {"$set": {"players.$.state": new_state}}
            )
            
            if result.modified_count == 0:
                raise ValueError("Failed to update ready state")
            
            # Get updated room
            updated_room = await RoomService.get_room(room_code)
            
            # Direct broadcast instead of using broadcast_room_update
            await manager.broadcast_to_room(
                room_code,
                {
                    "type": "room_update",
                    "event": "player_ready_changed",
                    "room": updated_room.model_dump(),
                    "timestamp": datetime.now().isoformat(),
                    "players": [
                        {
                            "user_id": p.user_id,
                            "nickname": p.nickname,
                            "state": p.state,
                            "is_host": p.user_id == updated_room.host
                        }
                        for p in updated_room.players
                    ],
                    "player": {
                        "user_id": str(user.id),
                        "nickname": user.nickname,
                        "new_state": new_state
                    }
                }
            )
            
            return updated_room
            
        except Exception as e:
            print(f"❌ Error in toggle_ready: {e}")
            raise

    @staticmethod
    async def leave_room(room_code: str, user: User) -> Room:
        try:
            # Check if room exists
            room = await RoomService.get_room(room_code)
            if not room:
                raise ValueError("Room not found")
            
            # Check if user is in the room
            if not any(p.user_id == str(user.id) for p in room.players):
                raise ValueError("User not in room")
            
            # Store if user was host before removing
            was_host = room.host == str(user.id)
            
            # Remove player from room
            result = await mongodb.db.rooms.update_one(
                {"code": room_code},
                {"$pull": {"players": {"user_id": str(user.id)}}}
            )
            
            if result.modified_count == 0:
                raise ValueError("Failed to leave room")
            
            # Get updated room state
            updated_room = await RoomService.get_room(room_code)
            
            # If room is empty or user was host
            if not updated_room.players:
                # Delete room if empty
                await mongodb.db.rooms.delete_one({"code": room_code})
                # Broadcast room deletion
                await manager.broadcast_to_room(
                    room_code,
                    {
                        "type": "room_update",
                        "event": "room_deleted",
                        "timestamp": datetime.now().isoformat(),
                        "room_code": room_code
                    }
                )
                return updated_room
            elif was_host:
                # Assign new host if previous host left
                new_host = updated_room.players[0].user_id
                await mongodb.db.rooms.update_one(
                    {"code": room_code},
                    {"$set": {"host": new_host}}
                )
                updated_room = await RoomService.get_room(room_code)
            
            # Broadcast player left update
            await manager.broadcast_to_room(
                room_code,
                {
                    "type": "room_update",
                    "event": "player_left",
                    "room": updated_room.model_dump(),
                    "timestamp": datetime.now().isoformat(),
                    "players": [
                        {
                            "user_id": p.user_id,
                            "nickname": p.nickname,
                            "state": p.state,
                            "is_host": p.user_id == updated_room.host
                        }
                        for p in updated_room.players
                    ],
                    "player": {
                        "user_id": str(user.id),
                        "nickname": user.nickname
                    }
                }
            )
            
            return updated_room
            
        except Exception as e:
            print(f"Error in leave_room: {e}")
            raise
    
    @staticmethod
    async def start_game(room_code: str, user: User) -> Room:
        try:
            room = await RoomService.get_room(room_code)
            if not room:
                raise ValueError("Room not found")
            
            if room.host != str(user.id):
                raise ValueError("Only the host can start the game")
            
            # Assign roles randomly
            players = room.players.copy()
            random.shuffle(players)
            
            roles = room.game_config["roles"]
            assigned_roles = []
            
            # Assign mafia roles
            mafia_players = players[:roles["mafia"]]
            for player in mafia_players:
                assigned_roles.append({
                    "player_id": player.user_id,
                    "role": "mafia",
                    "description": "Eliminate the civilians without getting caught.",
                    "teammates": [{"nickname": p.nickname} for p in mafia_players if p.user_id != player.user_id]
                })
            
            # Assign special roles
            current_index = roles["mafia"]
            
            if roles.get("doctor", 0):
                assigned_roles.append({
                    "player_id": players[current_index].user_id,
                    "role": "doctor",
                    "description": "Save one person each night from being eliminated.",
                    "teammates": []
                })
                current_index += 1
            
            if roles.get("police", 0):
                assigned_roles.append({
                    "player_id": players[current_index].user_id,
                    "role": "police",
                    "description": "Investigate one person each night to determine if they are mafia.",
                    "teammates": []
                })
                current_index += 1
            
            # Remaining players are civilians
            for player in players[current_index:]:
                assigned_roles.append({
                    "player_id": player.user_id,
                    "role": "civilian",
                    "description": "Find and eliminate the mafia before they eliminate you.",
                    "teammates": []
                })
            
            # Update room state and store roles
            await mongodb.db.rooms.update_one(
                {"code": room_code},
                {
                    "$set": {
                        "room_state": "in_game",
                        "game_state": {
                            "phase": "night",
                            "round": 1,
                            "roles": assigned_roles
                        }
                    }
                }
            )
            
            # First broadcast game start to all players
            await manager.broadcast_to_room(
                room_code,
                {
                    "type": "room_update",
                    "event": "game_started",
                    "room": room.model_dump(),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Log role assignments
            print(f"🎲 Role assignments for room {room_code}:")
            for role in assigned_roles:
                print(f"👤 Player {role['player_id']}: {role['role']}")

            # Send individual role information
            for role in assigned_roles:
                print(f"📤 Sending role to player {role['player_id']}")
                await manager.send_to_user(
                    room_code,
                    role["player_id"],
                    {
                        "type": "game_update",
                        "event": "role_assigned",
                        "player_id": role["player_id"],
                        "player_role": role
                    }
                )
                print(f"✅ Role sent to player {role['player_id']}")
            
            return await RoomService.get_room(room_code)
            
        except Exception as e:
            print(f"Error starting game: {e}")
            raise