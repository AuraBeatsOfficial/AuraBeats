"""Raw settings collection helpers (used by core/settings)."""
from core.database import db
from utils.logger import get_logger

log = get_logger("AuraBeats.DB.Settings")
_mem: dict = {}


async def get_setting(chat_id, key, default=None):
    if chat_id in _mem and key in _mem[chat_id]:
        return _mem[chat_id][key]
    if db.online:
        try:
            doc = await db.settings.find_one({"chat_id": chat_id})
            if doc and key in doc:
                _mem.setdefault(chat_id, {})[key] = doc[key]
                return doc[key]
        except Exception:
            pass
    return default


async def set_setting(chat_id, key, value):
    _mem.setdefault(chat_id, {})[key] = value
    if db.online:
        try:
            await db.settings.update_one(
                {"chat_id": chat_id},
                {"$set": {key: value}},
                upsert=True,
            )
            return True
        except Exception as e:
            log.warning(f"set_setting: {e}")
            return False
    return True


async def get_all_settings(chat_id) -> dict:
    out = {}
    if db.online:
        try:
            doc = await db.settings.find_one({"chat_id": chat_id})
            if doc:
                doc.pop("_id", None)
                doc.pop("chat_id", None)
                out.update(doc)
        except Exception:
            pass
    out.update(_mem.get(chat_id, {}))
    return out


async def reset_settings(chat_id):
    _mem.pop(chat_id, None)
    if db.online:
        try:
            await db.settings.delete_one({"chat_id": chat_id})
        except Exception:
            pass
    return True
