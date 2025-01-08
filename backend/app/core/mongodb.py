from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect_db(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
        print(f"Connected to MongoDB at {settings.MONGODB_URL}")

    async def close_db(self):
        if self.client is not None:
            self.client.close()
            print("Closed MongoDB connection")


mongodb = MongoDB()
