from fastapi import FastAPI
from contextlib import asynccontextmanager
from api import game_router, auth_router, room_router
from core.config import settings
from core.mongodb import mongodb
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.middlewares import StaticFilesCORSMiddleware
from pathlib import Path

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await mongodb.connect_db()
    yield
    # Shutdown
    await mongodb.close_db()

app = FastAPI(title="Buzz API", lifespan=lifespan)

# General CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(game_router, tags=["games"])
app.include_router(auth_router, tags=["auth"])
app.include_router(room_router, tags=["room"])
