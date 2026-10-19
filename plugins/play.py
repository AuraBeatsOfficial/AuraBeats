"""AuraBeats - /play handler (audio streaming)."""
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES
from core.calls import call_py, active_chats, queues, push_track
from utils.decorators import require_assistant
from utils.yt_helper import search
from utils.errors import SearchFailed
from utils.streamer import build_audio, build_video
from utils.inline_ui import now_playing, queued
from utils.keyboard import player
from utils.logger import get_logger

log = get_logger("AuraBeats.Play")


async def _handle_play(client, message: Message, is_video: bool = False):
    """Shared /play + /vplay logic."""
    cmd = "vplay" if is_video else "play"

    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            f"📝 **Usage:** `/{cmd} <song name or link>`"
        )

    query = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not query and message.reply_to_message and message.reply_to_message.text:
        query = message.reply_to_message.text

    status = await message.reply_text("🔍 **Searching…**")

    try:
        info = await search(query)
    except SearchFailed as e:
        return await status.edit_text(f"❌ **Search failed:**\n`{e}`")
    except Exception as e:
        log.exception(f"search error: {e}")
        return await status.edit_text(f"❌ `{e}`")

    chat_id = message.chat.id
    track = {
        "title":     info["title"],
        "url":       info["url"],
        "webpage":   info.get("webpage"),
        "duration":  info.get("duration", 0),
        "thumbnail": info.get("thumbnail"),
        "uploader":  info.get("uploader"),
        "views":     info.get("views", 0),
        "requester": message.from_user.mention if message.from_user else "—",
    }

    # Already playing → queue it
    if chat_id in active_chats:
        if not push_track(chat_id, track):
            return await status.edit_text("⚠️ **Queue is full.**")
        pos = len(queues.get(chat_id, []))
        return await status.edit_text(queued(track, pos))

    # Fresh stream
    try:
        await status.edit_text(f"🎶 **Connecting…**\n\n**{info['title']}**")
        stream = build_video(track["url"]) if is_video else build_audio(track["url"])

        try:
            await call_py.play(chat_id, stream)
        except Exception as e:
            err = str(e).lower()
            # Common: assistant not in VC / group
            if "not in" in err or "join" in err or "call" in err:
                raise RuntimeError(
                    "Assistant is not in the voice chat.\n"
                    "Add assistant to group and start a VC first."
                )
            raise

        active_chats[chat_id] = track
        await status.edit_text(
            now_playing(track),
            reply_markup=player(paused=False),
            disable_web_page_preview=True,
        )
    except Exception as e:
        log.exception(f"play failed: {e}")
        await status.edit_text(f"❌ **Playback failed:**\n`{e}`")


@Client.on_message(filters.command("play", PREFIXES) & filters.group)
@require_assistant
async def play_cmd(client, message: Message):
    await _handle_play(client, message, is_video=False)
