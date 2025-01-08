#!/usr/bin/env python3
import asyncio
import typer
from typing import List
from app.core.redis import redis_client
from app.models.game import Game

app = typer.Typer()

GAMES_KEY = "games"

INITIAL_GAMES = [
    {
        "name": "Mafia",
        "description": "A social deduction game where innocent civilians try to identify the mafia among them while the mafia tries to remain hidden.",
        "thumbnail_url": "/static/images/games/mafia-thumbnail.webp",
        "image_url": "/static/images/games/mafia.webp",
        "category": "social-deduction",
        "min_players": 6,
        "max_players": 12,
        "duration_minutes": 30
    },
    {
        "name": "Spyfall",
        "description": "Players try to discover who the spy is while the spy tries to figure out the location without revealing their identity.",
        "thumbnail_url": "/static/images/games/spyfall-thumbnail.webp",
        "image_url": "/static/images/games/spyfall.webp",
        "category": "social-deduction",
        "min_players": 4,
        "max_players": 8,
        "duration_minutes": 10
    }
]

async def init_games():
    """Initialize the games in Redis"""
    redis = redis_client.redis
    
    # Clear existing games
    await redis.delete(GAMES_KEY)
    
    # Create and store new games
    for game_data in INITIAL_GAMES:
        game = Game(**game_data)
        await redis.hset(GAMES_KEY, str(game.id), game.model_dump_json())
    
    print(f"Successfully initialized {len(INITIAL_GAMES)} games in Redis")

@app.command()
def main():
    """Initialize games data in Redis"""
    asyncio.run(init_games())

if __name__ == "__main__":
    app()
