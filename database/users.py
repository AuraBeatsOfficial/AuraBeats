"""Users collection - async helpers with memory fallback."""
from core.database import db
from utils.logger import get_logger

log = get_logger("AuraBeats.DB.Users")
_mem: dict = {}


async def save_user(uid, username=None, first_name=None):
    data = {"user_id": uid}
    if username: data["username"] = username
    if first_name: data["first_name"] = first_name
    _mem[uid] = {**_mem.get(uid, {}), **data}
    if db.online:
        try:
            await db.users.update_one({"user_id": uid}, {"$set": data}, upsert=True)
        except Exception as e:
            log.warning(f"save_user: {e}")
    return data


async def get_user(uid):
    if db.online:
        try:
            doc = await db.users.find_one({"user_id": uid})
            if doc:
                doc.pop("_id", None)
                return doc
        except Exception:
            pass
    return _mem.get(uid)


async def update_user(uid, **fields):
    _mem.setdefault(uid, {}).update(fields)
    if db.online:
        try:
            await db.users.update_one({"user_id": uid}, {"$set": fields}, upsert=True)
            return True
        except Exception as e:
            log.warning(f"update_user: {e}")
            return False
    return True


async def count_users():
    if db.online:
        try:
            return await db.users.count_documents({})
        except Exception:
            pass
    return len(_mem)


async def ban_user(uid):
    return await update_user(uid, banned=True)


async def unban_user(uid):
    return await update_user(uid, banned=False)


async def is_banned(uid):
    u = await get_user(uid)
    return bool(u and u.get("banned"))
