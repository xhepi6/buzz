from typing import List, Dict
from random import shuffle
from models.mafia import MafiaPlayer, MafiaRole, ROLE_DESCRIPTIONS
from models.room import Room

class MafiaService:
    @staticmethod
    def assign_roles(room: Room) -> List[MafiaPlayer]:
        """Assign roles to players in the room"""
        try:
            print(f"🎲 Assigning roles for room {room.code}")
            print(f"📊 Game config: {room.game_config}")
            
            roles = room.game_config.get("roles")
            if not roles:
                raise ValueError("No roles configuration found in game_config")
            
            players = room.players
            print(f"👥 Players to assign: {len(players)}")
            
            # Validate role counts
            total_roles = (
                roles.get("mafia", 0) +
                roles.get("civilian", 0) +
                roles.get("doctor", 0) +
                roles.get("police", 0)
            )
            
            if total_roles != len(players):
                raise ValueError(f"Role count ({total_roles}) doesn't match player count ({len(players)})")
            
            # Create role list based on configuration
            role_list = []
            role_mapping = {
                "mafia": MafiaRole.MAFIA,
                "civilian": MafiaRole.CIVILIAN,
                "doctor": MafiaRole.DOCTOR,
                "police": MafiaRole.POLICE
            }
            
            for role_type, count in roles.items():
                if role_type in role_mapping:
                    role_list.extend([role_mapping[role_type]] * count)
                else:
                    print(f"⚠️ Skipping invalid role type: {role_type}")
            
            if not role_list:
                raise ValueError("No valid roles could be assigned")
                
            print(f"🎭 Role list created: {role_list}")
            shuffle(role_list)
            
            # Create MafiaPlayer instances
            mafia_players: List[MafiaPlayer] = []
            mafia_members: List[str] = []
            
            for i, player in enumerate(players):
                role = role_list[i]
                print(f"👤 Assigning {role} to player {player.nickname}")
                
                # Track mafia members for teammate assignment
                if role == MafiaRole.MAFIA:
                    mafia_members.append(player.nickname)
                
                # Create role info with base description
                role_info = ROLE_DESCRIPTIONS[role].model_copy()
                
                # Add teammates for mafia members
                if role == MafiaRole.MAFIA:
                    role_info.teammates = [name for name in mafia_members if name != player.nickname]
                
                mafia_player = MafiaPlayer(
                    user_id=player.user_id,
                    nickname=player.nickname,
                    role_info=role_info
                )
                mafia_players.append(mafia_player)
            
            print(f"✅ Role assignment complete. {len(mafia_players)} players assigned")
            return mafia_players
            
        except Exception as e:
            print(f"❌ Error in assign_roles: {str(e)}")
            raise

    @staticmethod
    def create_game_state(players: List[MafiaPlayer]) -> Dict:
        """Create initial game state"""
        try:
            # Serialize players with proper role handling
            serialized_players = []
            for player in players:
                player_data = player.model_dump()
                if player_data.get('role_info') and player_data['role_info'].get('role'):
                    # Only convert to value if it's an Enum
                    if hasattr(player_data['role_info']['role'], 'value'):
                        player_data['role_info']['role'] = player_data['role_info']['role'].value
                serialized_players.append(player_data)

            game_state = {
                "phase": "night",
                "round": 1,
                "players": serialized_players,
                "eliminated_players": [],
                "votes": {},
                "night_actions": {}
            }
            print(f"🎮 Created game state: {game_state}")
            return game_state
            
        except Exception as e:
            print(f"❌ Error creating game state: {str(e)}")
            raise 