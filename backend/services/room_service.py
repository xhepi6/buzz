from typing import Optional
from bson.objectid import ObjectId
from core.mongodb import mongodb
from models.room import Room, RoomCreate, PlayerState
from models.user import User
import random
import string
from core.websocket import manager
from datetime import datetime
from services.mafia_service import MafiaService
from models.mafia import MafiaRole
from services.spyfall_service import SpyfallService

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
                # Ensure players exists and is a list
                if 'players' not in room_doc or room_doc['players'] is None:
                    room_doc['players'] = []
                
                # Enrich each player with user data
                enriched_players = []
                for player in room_doc['players']:
                    try:
                        enriched_player = await RoomService._enrich_player_data(player)
                        enriched_players.append(enriched_player)
                    except Exception as e:
                        print(f"❌ Error enriching player data: {e}")
                        continue
                    
                room_doc['players'] = enriched_players
                
                # Convert _id to string
                room_doc['_id'] = str(room_doc['_id'])
                
                # Handle game state if it exists
                if 'game_state' in room_doc and room_doc['game_state']:
                    game_state = room_doc['game_state']
                    # Ensure players exists in game state
                    if 'players' in game_state:
                        for player in game_state['players']:
                            if player.get('role_info') and isinstance(player['role_info'].get('role'), dict):
                                player['role_info']['role'] = player['role_info']['role'].get('value')
                    room_doc['game_state'] = game_state
                else:
                    room_doc['game_state'] = None
                
                print(f"📦 Room data before creating model: {room_doc}")
                return Room(**room_doc)
            return None
        except Exception as e:
            print(f"❌ Error getting room: {e}")
            print(f"Room document: {room_doc if 'room_doc' in locals() else 'Not found'}")
            raise
    
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
            await manager.broadcast_to_lobby(
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
            await manager.broadcast_to_lobby(
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
                await manager.broadcast_to_lobby(
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
            await manager.broadcast_to_lobby(
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
            print(f"🎮 Starting game for room {room_code}")
            room = await RoomService.get_room(room_code)
            if not room:
                raise ValueError("Room not found")
            
            print(f"👥 Room found with {len(room.players)} players")
            
            if room.host != str(user.id):
                raise ValueError("Only the host can start the game")
            
            if not all(p.state == "ready" for p in room.players):
                raise ValueError("Not all players are ready")
            
            if len(room.players) != room.num_players:
                raise ValueError("Not all players have joined")
            
            # Initialize game state based on game type
            if room.game_type == "mafia":
                print(f"🎲 Initializing Mafia game")
                try:
                    mafia_players = MafiaService.assign_roles(room)
                    game_state = MafiaService.create_game_state(mafia_players)
                    
                    print(f"💾 Updating room state in database")
                    # Update room with game state
                    result = await mongodb.db.rooms.update_one(
                        {"code": room_code},
                        {"$set": {
                            "room_state": "in_game",
                            "game_state": game_state
                        }}
                    )
                    
                    if result.modified_count == 0:
                        raise ValueError("Failed to update room state")
                    
                    print(f"📢 Broadcasting game start")
                    # Broadcast game started to all players
                    await manager.broadcast_to_lobby(
                        room_code,
                        {
                            "type": "game_started",
                            "game_type": room.game_type,
                            "room_code": room.code
                        }
                    )
                    
                    print(f"📨 Sending individual role information")
                    # Send individual role information
                    for player in mafia_players:
                        try:
                            role_info = player.role_info.model_dump()
                            # Only convert to value if it's an Enum
                            if isinstance(role_info.get('role'), MafiaRole):
                                role_info['role'] = role_info['role'].value
                                
                            print(f"  -> Sending role to {player.nickname}: {role_info}")
                            await manager.send_to_user(
                                room_code,
                                player.user_id,
                                {
                                    "type": "game_update",
                                    "event": "role_assigned",
                                    "player_id": player.user_id,
                                    "role_info": role_info
                                },
                                'lobby'  # Send through lobby connection since game connection isn't established yet
                            )
                        except Exception as e:
                            print(f"❌ Error sending role to {player.nickname}: {str(e)}")
                            raise
                    
                    return await RoomService.get_room(room_code)
                    
                except Exception as e:
                    print(f"❌ Error in Mafia game initialization: {str(e)}")
                    raise ValueError(f"Failed to initialize Mafia game: {str(e)}")
            elif room.game_type == "spyfall":
                print(f"🎲 Initializing Spyfall game")
                try:
                    spyfall_players, location = SpyfallService.assign_roles(room)
                    game_state = SpyfallService.create_game_state(
                        spyfall_players,
                        location,
                        room.game_config.get("roundMinutes", 8)
                    )
                    
                    # Update room with game state
                    result = await mongodb.db.rooms.update_one(
                        {"code": room_code},
                        {"$set": {
                            "room_state": "in_game",
                            "game_state": game_state
                        }}
                    )
                    
                    if result.modified_count == 0:
                        raise ValueError("Failed to update room state")
                    
                    # Broadcast game started
                    await manager.broadcast_to_lobby(
                        room_code,
                        {
                            "type": "game_started",
                            "game_type": room.game_type,
                            "room_code": room.code
                        }
                    )
                    
                    # Send individual role information
                    for player in spyfall_players:
                        await manager.send_to_user(
                            room_code,
                            player.user_id,
                            {
                                "type": "game_update",
                                "event": "role_assigned",
                                "player_id": player.user_id,
                                "role_info": player.role_info.model_dump()
                            },
                            'lobby'
                        )
                    
                    return await RoomService.get_room(room_code)
                    
                except Exception as e:
                    print(f"❌ Error in Spyfall game initialization: {str(e)}")
                    raise ValueError(f"Failed to initialize Spyfall game: {str(e)}")
            else:
                raise ValueError(f"Unsupported game type: {room.game_type}")
            
        except Exception as e:
            print(f"❌ Error in start_game: {str(e)}")
            raise

    @staticmethod
    async def restart_game(room_code: str, user: User) -> Room:
        try:
            print(f"🔄 Attempting to restart game for room: {room_code}")
            room = await RoomService.get_room(room_code)
            if not room:
                raise ValueError("Room not found")
            
            if room.host != str(user.id):
                raise ValueError("Only the host can restart the game")
            
            # Get current players before resetting
            current_players = []
            if hasattr(room, 'players') and room.players:
                for player in room.players:
                    try:
                        player_data = {
                            "user_id": str(player.user_id),  # Ensure user_id is string
                            "nickname": player.nickname,
                            "full_name": getattr(player, 'full_name', None),
                            "email": getattr(player, 'email', None),
                            "state": "not_ready"
                        }
                        current_players.append(player_data)
                        print(f"✅ Processed player: {player_data}")
                    except Exception as e:
                        print(f"❌ Error processing player {player}: {str(e)}")
                        continue
            
            print(f"🔄 Resetting room with {len(current_players)} players")
            
            # Reset room state
            update_data = {
                "room_state": "lobby",
                "game_state": None,
                "players": current_players
            }
            
            # Update the room
            result = await mongodb.db.rooms.update_one(
                {"code": room_code},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                print("⚠️ No modifications made to room")
                # Get the current room state to verify
                current_room = await mongodb.db.rooms.find_one({"code": room_code})
                print(f"Current room state: {current_room}")
                raise ValueError("Failed to restart game")
            
            # Get and return updated room
            updated_room = await RoomService.get_room(room_code)
            if not updated_room:
                raise ValueError("Failed to get updated room state")
            
            print(f"✅ Room {room_code} successfully restarted")
            return updated_room
            
        except Exception as e:
            print(f"❌ Error restarting game: {str(e)}")
            raise