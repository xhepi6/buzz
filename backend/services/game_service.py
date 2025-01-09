from typing import List, Optional
from bson.objectid import ObjectId
from core.mongodb import mongodb
from models.game import Game

class GameService:
    @staticmethod
    async def get_games(category: Optional[str] = None) -> List[Game]:
        query = {"category": category} if category else {}
        cursor = mongodb.db.games.find(query)
        games = []
        async for doc in cursor:
            games.append(Game.model_validate(doc))
        return games

    @staticmethod
    async def get_game(game_id: str) -> Optional[Game]:
        try:
            game_doc = await mongodb.db.games.find_one({"_id": ObjectId(game_id)})
            return Game.model_validate(game_doc) if game_doc else None
        except Exception as e:
            print(f"Error getting game: {e}")
            return None

    @staticmethod
    async def get_categories() -> List[str]:
        return await mongodb.db.games.distinct("category")
