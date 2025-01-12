from typing import List, Optional
from models.game import Game
from services.game_service import GameService
from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/games", response_model=List[Game])
async def get_games(category: Optional[str] = None):
    logger.debug("Getting games with category: %s", category)
    return await GameService.get_games(category)

@router.get("/games/{game_id}", response_model=Game)
async def get_game(game_id: str):
    logger.debug("Getting game with ID: %s", game_id)
    game = await GameService.get_game(game_id)
    if not game:
        logger.warning("Game not found: %s", game_id)
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.get("/categories", response_model=List[str])
async def get_categories():
    logger.debug("Getting game categories")
    return await GameService.get_categories()

