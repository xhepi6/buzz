from pathlib import Path

from api import game_router, auth_router, room_router
from core.config import settings
from core.mongodb import mongodb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
app.include_router(game_router, tags=["games"])
app.include_router(auth_router, tags=["auth"])
app.include_router(room_router, tags=["room"])

@app.on_event("startup")
async def startup_db_client():
    await mongodb.connect_db()

@app.on_event("shutdown")
async def shutdown_db_client():
    await mongodb.close_db()
