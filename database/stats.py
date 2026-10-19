"""Analytics - counters and top tracks."""
from core.database import db
from utils.logger import get_logger

log = get_logger("AuraBeats.DB.Stats")
_mem = {"plays": 0, "tracks": {}}


async def increment_play(chat_id=None, title=None):
    _mem["plays"] += 1
    if title:
        _mem["tracks"][title] = _mem["tracks"].get(title, 0) + 1
    if db.online:
        try:
            await db.stats.update_one(
                {"_id": "global"},
                {"$inc": {"plays": 1}},
                upsert=True,
            )
            if title:
                await db.stats.update_one(
                    {"_id": f"track:{title}"},
                    {"$inc": {"count": 1}},
                    upsert=True,
                )
        except Exception as e:
            log.warning(f"increment_play: {e}")


async def total_plays() -> int:
    if db.online:
        try:
            doc = await db.stats.find_one({"_id": "global"})
            if doc:
                return doc.get("plays", 0)
        except Exception:
            pass
    return _mem["plays"]


async def top_tracks(limit: int = 10) -> list:
    if db.online:
        try:
            out = []
            async for d in db.stats.find({"_id": {"$regex": "^track:"}}).sort("count", -1).limit(limit):
                out.append((d["_id"].replace("track:", ""), d.get("count", 0)))
            if out:
                return out
        except Exception:
            pass
    items = sorted(_mem["tracks"].items(), key=lambda x: -x[1])
    return items[:limit]


async def record_play(chat_id, title, requester=None):
    """Full play record — tracks per chat and requester."""
    await increment_play(chat_id, title)
    if db.online:
        try:
            await db.stats.insert_one({
                "chat_id": chat_id, "title": title, "requester": requester,
            })
        except Exception:
            pass
