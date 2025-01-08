from typing import List, Optional
from bson import ObjectId
from app.core.mongodb import mongodb
from app.models.game import Game

class GameService:
    @staticmethod
    async def get_games(category: Optional[str] = None) -> List[Game]:
        query = {"category": category} if category else {}
        cursor = mongodb.db.games.find(query)
        games = []
        async for game_doc in cursor:
            # Convert ObjectId to string for the id field
            game_doc["id"] = str(game_doc.pop("_id"))
            games.append(Game(**game_doc))
        return games

    @staticmethod
    async def get_game(game_id: str) -> Optional[Game]:
        try:
            game_doc = await mongodb.db.games.find_one({"_id": ObjectId(game_id)})
            if game_doc:
                game_doc["id"] = str(game_doc.pop("_id"))
                return Game(**game_doc)
        except:
            pass
        return None

    @staticmethod
    async def get_categories() -> List[str]:
        categories = await mongodb.db.games.distinct("category")
        return categories
