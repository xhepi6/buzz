from typing import List, Dict, Optional
from random import choice, shuffle
from models.spyfall import SpyfallPlayer, SpyfallRole, SpyfallRoleInfo
from models.room import Room
from datetime import datetime, timedelta
from services.game_service import GameService
import logging

logger = logging.getLogger(__name__)

class SpyfallService:
    @staticmethod
    async def assign_roles(room: Room) -> tuple[List[SpyfallPlayer], str]:
        """Assign roles to players and select location"""
        try:
            logger.info("Assigning roles for room %s", room.code)
            
            # Get game data for location images
            game = await GameService.get_game("spyfall")
            if not game:
                raise ValueError("Spyfall game configuration not found")
                
            logger.info("🎮 Game data received:", game.model_dump())
            
            # Get game configuration
            spy_count = room.game_config.get("spyCount", 1)
            use_custom_locations = room.game_config.get("useCustomLocations", False)
            custom_locations = room.game_config.get("customLocations", [])
            
            # Get available locations from game data
            available_locations = list(game.locations.keys())
            locations = custom_locations if use_custom_locations and custom_locations else available_locations
            selected_location = choice(locations)
            logger.debug("Selected location: %s", selected_location)
            
            # Get location image if available
            location_image = game.locations.get(selected_location) if game.locations else None
            logger.info(f"🎯 Selected location image: {location_image}")
            
            if not location_image:
                logger.warning(f"⚠️ No image found for location {selected_location}")
                logger.warning(f"⚠️ Available locations: {available_locations}")
            
            # Prepare player list
            players = list(room.players)
            shuffle(players)
            
            # Assign roles
            spyfall_players: List[SpyfallPlayer] = []
            
            # Assign spies first
            for i in range(spy_count):
                if i < len(players):
                    player = players[i]
                    spyfall_players.append(SpyfallPlayer(
                        user_id=player.user_id,
                        nickname=player.nickname,
                        role_info=SpyfallRoleInfo(
                            role=SpyfallRole.SPY,
                            description="You are the Spy! Try to figure out the location while avoiding detection."
                        )
                    ))
            
            # Assign regular players
            for player in players[spy_count:]:
                spyfall_players.append(SpyfallPlayer(
                    user_id=player.user_id,
                    nickname=player.nickname,
                    role_info=SpyfallRoleInfo(
                        role=SpyfallRole.REGULAR,
                        location=selected_location,
                        location_image=location_image,
                        description=f"You are at the {selected_location}. Find the spy!"
                    )
                ))
            
            # Debug log for role assignments
            for player in spyfall_players:
                logger.info(f"🎭 Role assigned to {player.nickname}:", {
                    "role": player.role_info.role,
                    "location": player.role_info.location,
                    "has_image": bool(player.role_info.location_image)
                })
            
            shuffle(spyfall_players)  # Shuffle again to hide spy positions
            return spyfall_players, selected_location
            
        except Exception as e:
            logger.error("Error in assign_roles: %s", str(e))
            raise

    @staticmethod
    def create_game_state(players: List[SpyfallPlayer], location: str, round_minutes: int) -> Dict:
        """Create initial game state"""
        try:
            # Calculate round end time
            # Ensure we're using UTC time
            current_time = datetime.utcnow()
            round_end_time = (current_time + timedelta(minutes=2)).isoformat() + 'Z'
            
            # Serialize players with proper role handling
            serialized_players = []
            for player in players:
                player_data = player.model_dump()
                serialized_players.append(player_data)

            game_state = {
                "players": serialized_players,
                "location": location,
                "round_end_time": round_end_time
            }
            
            logger.info(f"🎮 Created Spyfall game state with UTC end time: {round_end_time}")
            return game_state
            
        except Exception as e:
            logger.error("Error creating game state: %s", str(e))
            raise 