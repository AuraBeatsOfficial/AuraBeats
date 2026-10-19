"""Persistent queue collection - survives restarts."""
from core.database import db
from utils.logger import get_logger

log = get_logger("AuraBeats.DB.Queue")
_mem: dict = {}


async def save_queue(chat_id, queue: list):
    _mem[chat_id] = list(queue)
    if db.online:
        try:
            await db.queue.update_one(
                {"chat_id": chat_id},
                {"$set": {"tracks": queue}},
                upsert=True,
            )
        except Exception as e:
            log.warning(f"save_queue: {e}")
    return True


async def load_queue(chat_id) -> list:
    if db.online:
        try:
            doc = await db.queue.find_one({"chat_id": chat_id})
            if doc:
                return doc.get("tracks", [])
        except Exception:
            pass
    return _mem.get(chat_id, [])


async def clear_queue(chat_id):
    _mem.pop(chat_id, None)
    if db.online:
        try:
            await db.queue.delete_one({"chat_id": chat_id})
        except Exception:
            pass
    return True


async def all_saved_queues() -> dict:
    if db.online:
        try:
            return {d["chat_id"]: d.get("tracks", [])
                    async for d in db.queue.find({})}
        except Exception:
            pass
    return dict(_mem)
