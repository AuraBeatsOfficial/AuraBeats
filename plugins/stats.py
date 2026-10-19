"""AuraBeats - /stats analytics and health."""
import time
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, BOT_NAME
from core.calls import active_chats, queues
from core.database import db
from database.users import count_users
from database.chats import count_chats
from database.stats import total_plays, top_tracks
from utils.formatters import humanize_duration, compact_number

_START = time.time()


@Client.on_message(filters.command("stats", PREFIXES))
async def stats_cmd(client, message: Message):
    uptime = int(time.time() - _START)
    users = await count_users()
    chats = await count_chats()
    plays = await total_plays()

    text = (
        f"**📊 {BOT_NAME} — Stats**\n\n"
        f"**⏱ Uptime:** `{humanize_duration(uptime)}`\n"
        f"**👥 Users:** `{compact_number(users)}`\n"
        f"**💬 Chats:** `{compact_number(chats)}`\n"
        f"**🎵 Total Plays:** `{compact_number(plays)}`\n\n"
        f"**🎧 Active VCs:** `{len(active_chats)}`\n"
        f"**📋 Chats with queue:** `{len(queues)}`\n"
        f"**💾 DB:** `{'online' if db.online else 'offline (memory fallback)'}`"
    )
    await message.reply_text(text)


@Client.on_message(filters.command(["top", "toptracks"], PREFIXES))
async def top_cmd(client, message: Message):
    items = await top_tracks(10)
    if not items:
        return await message.reply_text("📭 No plays recorded yet.")
    lines = ["**🏆 Top Tracks**", ""]
    for i, (title, count) in enumerate(items, 1):
        lines.append(f"`{i}.` {title[:40]} — `{count} plays`")
    await message.reply_text("\n".join(lines))


@Client.on_message(filters.command("active", PREFIXES) & filters.private)
async def active_cmd(client, message: Message):
    """List all chats with active streams (sudo only ideally, but useful for debug)."""
    if not active_chats:
        return await message.reply_text("📭 No active voice chats.")
    lines = ["**🎧 Active Voice Chats**", ""]
    for cid, track in active_chats.items():
        q = len(queues.get(cid, []))
        lines.append(f"`{cid}` — {track.get('title','?')[:30]} (+{q})")
    await message.reply_text("\n".join(lines))
