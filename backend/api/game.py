from typing import List, Optional
from models.game import Game
from services.game_service import GameService
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os

router = APIRouter()

@router.get("/games", response_model=List[Game])
async def get_games(category: Optional[str] = None):
    return await GameService.get_games(category)

@router.get("/games/{game_id}", response_model=Game)
async def get_game(game_id: str):
    game = await GameService.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.get("/categories", response_model=List[str])
async def get_categories():
    return await GameService.get_categories()

@router.get("/debug/spyfall-images")
async def debug_spyfall_images():
    """Debug endpoint to check image paths"""
    static_path = Path(__file__).parent.parent / "static"
    spyfall_path = static_path / "images" / "spyfall_locations"
    
    if not spyfall_path.exists():
        return JSONResponse({
            "error": "Spyfall images directory not found",
            "path": str(spyfall_path)
        })
    
    files = list(spyfall_path.glob("*.webp"))
    
    if files:
        try:
            with open(files[0], 'rb') as f:
                _ = f.read(100)  # Try to read first 100 bytes
            file_stat = files[0].stat()
            file_info = {
                "size": file_stat.st_size,
                "permissions": oct(file_stat.st_mode)[-3:],
                "readable": os.access(files[0], os.R_OK)
            }
        except Exception as e:
            file_info = {"error": str(e)}
    else:
        file_info = {"error": "No files found"}
    
    return JSONResponse({
        "directory": str(spyfall_path),
        "exists": spyfall_path.exists(),
        "files": [f.name for f in files],
        "file_info": file_info,
        "directory_permissions": oct(spyfall_path.stat().st_mode)[-3:]
    })
