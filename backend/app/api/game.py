from typing import List, Optional
from uuid import UUID

from app.models.game import Game
from app.services.game_service import GameService
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/games", response_model=List[Game])
async def get_games(category: Optional[str] = None):
    return await GameService.get_games(category)

@router.get("/games/{game_id}", response_model=Game)
async def get_game(game_id: UUID):
    game = await GameService.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.get("/categories", response_model=List[str])
async def get_categories():
    return await GameService.get_categories()
