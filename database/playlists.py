"""Playlists collection - per-user playlists."""
from core.database import db
from utils.logger import get_logger

log = get_logger("AuraBeats.DB.Playlists")
_mem: dict = {}  # {user_id: {name: [tracks]}}


def _pl(user_id):
    return _mem.setdefault(user_id, {})


async def create_playlist(user_id, name):
    _pl(user_id).setdefault(name, [])
    if db.online:
        try:
            await db.playlists.update_one(
                {"user_id": user_id, "name": name},
                {"$setOnInsert": {"tracks": []}},
                upsert=True,
            )
        except Exception as e:
            log.warning(f"create_playlist: {e}")
    return True


async def add_track(user_id, name, track: dict):
    _pl(user_id).setdefault(name, []).append(track)
    if db.online:
        try:
            await db.playlists.update_one(
                {"user_id": user_id, "name": name},
                {"$push": {"tracks": track}},
                upsert=True,
            )
        except Exception as e:
            log.warning(f"add_track: {e}")
    return True


async def get_playlist(user_id, name):
    if db.online:
        try:
            doc = await db.playlists.find_one({"user_id": user_id, "name": name})
            if doc:
                return doc.get("tracks", [])
        except Exception:
            pass
    return _pl(user_id).get(name, [])


async def list_playlists(user_id):
    if db.online:
        try:
            return [d["name"] async for d in db.playlists.find(
                {"user_id": user_id}, {"name": 1})]
        except Exception:
            pass
    return list(_pl(user_id).keys())


async def delete_playlist(user_id, name):
    _pl(user_id).pop(name, None)
    if db.online:
        try:
            await db.playlists.delete_one({"user_id": user_id, "name": name})
        except Exception:
            pass
    return True


async def remove_track(user_id, name, index: int):
    tracks = _pl(user_id).get(name, [])
    if 0 <= index < len(tracks):
        tracks.pop(index)
    if db.online:
        try:
            doc = await db.playlists.find_one({"user_id": user_id, "name": name})
            if doc:
                t = doc.get("tracks", [])
                if 0 <= index < len(t):
                    t.pop(index)
                    await db.playlists.update_one(
                        {"user_id": user_id, "name": name},
                        {"$set": {"tracks": t}},
                    )
        except Exception:
            pass
    return True
