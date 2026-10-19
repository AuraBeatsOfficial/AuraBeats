"""
AuraBeats - Runtime Settings Store
In-memory cache backed by MongoDB.
"""
from core.database import db
from utils.logger import get_logger

log = get_logger("AuraBeats.Settings")

_cache: dict = {}
_defaults: dict = {
    "prefix": None,
    "volume": 100,
    "loop": "off",
    "autoplay": True,
    "language": "en",
    "feature_effects": True,
    "feature_ai": True,
}


async def get(chat_id: int, key: str, default=None):
    if chat_id in _cache and key in _cache[chat_id]:
        return _cache[chat_id][key]
    if db.online:
        try:
            doc = await db.settings.find_one({"chat_id": chat_id})
            if doc and key in doc:
                _cache.setdefault(chat_id, {})[key] = doc[key]
                return doc[key]
        except Exception as e:
            log.warning(f"settings get failed: {e}")
    if default is not None:
        return default
    return _defaults.get(key)


async def set(chat_id: int, key: str, value) -> bool:
    _cache.setdefault(chat_id, {})[key] = value
    if db.online:
        try:
            await db.settings.update_one(
                {"chat_id": chat_id},
                {"$set": {key: value}},
                upsert=True,
            )
            return True
        except Exception as e:
            log.warning(f"settings set failed: {e}")
    return False


async def get_all(chat_id: int) -> dict:
    merged = dict(_defaults)
    if db.online:
        try:
            doc = await db.settings.find_one({"chat_id": chat_id})
            if doc:
                doc.pop("_id", None)
                doc.pop("chat_id", None)
                merged.update(doc)
        except Exception:
            pass
    merged.update(_cache.get(chat_id, {}))
    return merged


async def reset(chat_id: int):
    _cache.pop(chat_id, None)
    if db.online:
        try:
            await db.settings.delete_one({"chat_id": chat_id})
        except Exception:
            pass
