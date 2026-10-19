"""Chats collection - group metadata + settings."""
from core.database import db
from utils.logger import get_logger

log = get_logger("AuraBeats.DB.Chats")
_mem: dict = {}


async def save_chat(chat_id, title=None, username=None):
    data = {"chat_id": chat_id}
    if title: data["title"] = title
    if username: data["username"] = username
    _mem[chat_id] = {**_mem.get(chat_id, {}), **data}
    if db.online:
        try:
            await db.chats.update_one({"chat_id": chat_id}, {"$set": data}, upsert=True)
        except Exception as e:
            log.warning(f"save_chat: {e}")
    return data


async def get_chat(chat_id):
    if db.online:
        try:
            doc = await db.chats.find_one({"chat_id": chat_id})
            if doc:
                doc.pop("_id", None)
                return doc
        except Exception:
            pass
    return _mem.get(chat_id)


async def update_chat(chat_id, **fields):
    _mem.setdefault(chat_id, {}).update(fields)
    if db.online:
        try:
            await db.chats.update_one({"chat_id": chat_id}, {"$set": fields}, upsert=True)
            return True
        except Exception as e:
            log.warning(f"update_chat: {e}")
            return False
    return True


async def count_chats():
    if db.online:
        try:
            return await db.chats.count_documents({})
        except Exception:
            pass
    return len(_mem)


async def get_all_chat_ids():
    if db.online:
        try:
            return [c["chat_id"] async for c in db.chats.find({}, {"chat_id": 1})]
        except Exception:
            pass
    return list(_mem.keys())
