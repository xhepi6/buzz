from uuid import UUID
from typing import List, Optional
from app.core.redis import redis_client
from app.models.game import Game

GAMES_KEY = "games"

class GameService:
    @staticmethod
    async def get_games(category: Optional[str] = None) -> List[Game]:
        redis = redis_client.redis
        games_data = await redis.hgetall(GAMES_KEY)
        games = [Game.model_validate_json(game_json) for game_json in games_data.values()]
        
        if category:
            games = [game for game in games if game.category == category]
        
        return games

    @staticmethod
    async def get_game(game_id: UUID) -> Optional[Game]:
        redis = redis_client.redis
        game_data = await redis.hget(GAMES_KEY, str(game_id))
        if game_data:
            return Game.model_validate_json(game_data)
        return None

    @staticmethod
    async def get_categories() -> List[str]:
        games = await GameService.get_games()
        return list(set(game.category for game in games))
