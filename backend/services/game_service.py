from typing import List, Optional
from models.game import Game
from core.mongodb import mongodb

class GameService:
    @staticmethod
    async def get_games(category: Optional[str] = None) -> List[Game]:
        query = {}
        if category:
            query["category"] = category
        games = await mongodb.db.games.find(query).to_list(length=None)
        return [Game(**game) for game in games]

    @staticmethod
    async def get_game(game_id: str) -> Optional[Game]:
        game = await mongodb.db.games.find_one({"_id": game_id})
        if game:
            return Game(**game)
        return None

    @staticmethod
    async def get_categories() -> List[str]:
        categories = await mongodb.db.games.distinct("category")
        return categories

    @staticmethod
    async def get_featured_games() -> List[Game]:
        featured_games = await mongodb.db.games.find({"featured": True}).to_list(length=None)
        return [Game(**game) for game in featured_games]
