from core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect_db(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
        logger.info("Connected to MongoDB at %s", settings.MONGODB_URL)

    async def close_db(self):
        if self.client is not None:
            self.client.close()
            logger.info("Closed MongoDB connection")


mongodb = MongoDB()
