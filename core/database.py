"""
AuraBeats - MongoDB Async Layer (Motor)
Graceful degradation if Mongo is offline.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, DB_NAME
from utils.logger import get_logger

log = get_logger("AuraBeats.DB")


class Database:
    """Async MongoDB wrapper with graceful failure."""

    def __init__(self):
        self.client = None
        self.db = None
        self.online = False

    async def connect(self) -> bool:
        try:
            self.client = AsyncIOMotorClient(
                MONGO_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            await self.client.admin.command("ping")
            self.db = self.client[DB_NAME]
            self.online = True
            log.info(f"MongoDB connected: {DB_NAME}")
            return True
        except Exception as e:
            log.warning(f"MongoDB offline — using memory fallback: {e}")
            self.online = False
            return False

    async def close(self):
        if self.client:
            try:
                self.client.close()
                log.info("MongoDB connection closed")
            except Exception:
                pass

    def _coll(self, name: str):
        if not self.online:
            return None
        return self.db[name]

    @property
    def users(self):       return self._coll("users")
    @property
    def chats(self):       return self._coll("chats")
    @property
    def playlists(self):   return self._coll("playlists")
    @property
    def queue(self):       return self._coll("queue")
    @property
    def settings(self):    return self._coll("settings")
    @property
    def stats(self):       return self._coll("stats")


db = Database()
