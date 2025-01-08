from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.redis import redis_client
from app.api import game
from fastapi.staticfiles import StaticFiles
from pathlib import Path


app = FastAPI(title="Buzz API")

static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(game.router, tags=["games"])

@app.on_event("startup")
async def startup_event():
    await redis_client.init_redis()

@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.close_redis()
