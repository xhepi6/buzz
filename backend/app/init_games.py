#!/usr/bin/env python3
import asyncio
from uuid import uuid4

import typer
from core.mongodb import mongodb

app = typer.Typer()

INITIAL_GAMES = [
    {
        "_id": str(uuid4()),
        "name": "Mafia",
        "description": (
            "A social deduction game where innocent civilians try to identify "
            "the mafia among them while the mafia tries to remain hidden."
        ),
        "min_players": 6,
        "max_players": 12,
        "category": "social-deduction",
        "duration_minutes": 30,
        "thumbnail_url": "/static/images/games/mafia-thumbnail.webp",
        "image_url": "/static/images/games/mafia.webp"
    },
    {
        "_id": str(uuid4()),
        "name": "Spyfall",
        "description": (
            "Players try to discover who the spy is while the spy tries to "
            "figure out the location without revealing their identity."
        ),
        "min_players": 4,
        "max_players": 8,
        "category": "social-deduction",
        "duration_minutes": 10,
        "thumbnail_url": "/static/images/games/spyfall-thumbnail.webp",
        "image_url": "/static/images/games/spyfall.webp"
    }
]


async def init_games():
    await mongodb.connect_db()

    # Clear existing games
    await mongodb.db.games.delete_many({})

    # Create and store new games
    await mongodb.db.games.insert_many(INITIAL_GAMES)

    print("Games initialized successfully!")

    # Print stored games for verification
    async for game in mongodb.db.games.find():
        print(f"\n{game['_id']}:")
        print(game)


@app.command()
def main():
    """Initialize games data in MongoDB"""
    asyncio.run(init_games())


if __name__ == "__main__":
    app()
