"""AuraBeats - /aimood AI playlist generator (query-based)."""
import random
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, FEATURE_AI
from core.calls import call_py, active_chats, push_track
from utils.decorators import require_assistant
from utils.yt_helper import search
from utils.streamer import build_audio
from utils.inline_ui import now_playing, queued
from utils.keyboard import player
from utils.logger import get_logger

log = get_logger("AuraBeats.AI")

# Curated mood seeds — real Hindi + English tracks
MOOD_SEEDS = {
    "happy":     ["kesariya arijit singh", "chaar kadam", "on top of the world"],
    "sad":       ["tum hi ho arijit singh", "channa mereya", "fix you coldplay"],
    "chill":     ["lofi hindi mix", "sunflower post malone", "araara arijit"],
    "party":     ["apna bana le", "shape of you", "kesariya remix"],
    "romantic":  ["tum kya mile", "perfect ed sheeran", "raataan lambiyan"],
    "workout":   ["believer imagine dragons", "titanium", "malhari"],
    "focus":     ["interstellar theme", "beethoven moonlight", "lofi study"],
    "sleep":     ["rain sounds relaxing", "ocean waves", "lofi sleep"],
}


@Client.on_message(filters.command("aimood", PREFIXES) & filters.group)
@require_assistant
async def aimood_cmd(client, message: Message):
    if not FEATURE_AI:
        return await message.reply_text("⚠️ AI module disabled.")

    if len(message.command) < 2:
        moods = " · ".join(f"`{m}`" for m in MOOD_SEEDS)
        return await message.reply_text(
            f"🧠 **AI Mood Playlist**\n\nMoods: {moods}\n\n"
            f"Usage: `/aimood <mood>`"
        )

    mood = message.command[1].lower()
    seeds = MOOD_SEEDS.get(mood)
    if not seeds:
        return await message.reply_text(f"❌ Unknown mood. Available: `{'`, `'.join(MOOD_SEEDS)}`")

    status = await message.reply_text(f"🧠 **Curating a `{mood}` playlist…**")
    chat_id = message.chat.id

    # pick 3 random seeds
    random.shuffle(seeds)
    picked = seeds[:3]
    found = []
    for q in picked:
        try:
            info = await search(q)
            found.append({
                "title":    info["title"],
                "url":      info["url"],
                "duration": info.get("duration", 0),
                "requester": f"AI {mood}",
            })
        except Exception as e:
            log.warning(f"seed failed {q}: {e}")

    if not found:
        return await status.edit_text("❌ AI couldn't find tracks. Try again later.")

    # stream first, queue rest
    first = found[0]
    try:
        await call_py.play(chat_id, build_audio(first["url"]))
        active_chats[chat_id] = first
        for t in found[1:]:
            push_track(chat_id, t)
        await status.edit_text(
            f"🧠 **AI {mood.title()} mix ready!**\n\n"
            f"🎶 Now: **{first['title'][:50]}**\n"
            f"📋 Queued: {len(found)-1} more",
            reply_markup=player(paused=False),
            disable_web_page_preview=True,
        )
    except Exception as e:
        log.exception(f"aimood play failed: {e}")
        await status.edit_text(f"❌ `{e}`")
