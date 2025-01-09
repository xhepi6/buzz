from .auth import router as auth_router
from .game import router as game_router
from .room import router as room_router

__all__ = ["auth_router", "game_router", "room_router"]
