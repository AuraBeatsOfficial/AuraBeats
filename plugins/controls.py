"""AuraBeats - /pause /resume /skip /stop /seek /volume."""
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES
from core.calls import call_py, active_chats, queues, paused, pop_next, clear_chat
from utils.decorators import require_assistant
from utils.formatters import parse_timestamp
from utils.streamer import build_audio
from utils.inline_ui import now_playing
from utils.keyboard import player
from utils.logger import get_logger

log = get_logger("AuraBeats.Controls")


# ---------- safe method wrappers (py-tgcalls version friendly) ----------
async def safe_pause(chat_id):
    if hasattr(call_py, "pause_stream"):
        await call_py.pause_stream(chat_id)
    else:
        await call_py.pause(chat_id)


async def safe_resume(chat_id):
    if hasattr(call_py, "resume_stream"):
        await call_py.resume_stream(chat_id)
    else:
        await call_py.resume(chat_id)


async def safe_leave(chat_id):
    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass


async def play_next(chat_id):
    """Pop next track from queue and stream it. Returns track or None."""
    nxt = pop_next(chat_id)
    if not nxt:
        await safe_leave(chat_id)
        active_chats.pop(chat_id, None)
        paused.discard(chat_id)
        return None
    try:
        await call_py.play(chat_id, build_audio(nxt["url"]))
        active_chats[chat_id] = nxt
        paused.discard(chat_id)
        return nxt
    except Exception as e:
        log.warning(f"play_next failed: {e}")
        return None


# ---------- /pause ----------
@Client.on_message(filters.command("pause", PREFIXES) & filters.group)
@require_assistant
async def pause_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in active_chats:
        return await message.reply_text("❌ Nothing is playing.")
    try:
        await safe_pause(chat_id)
        paused.add(chat_id)
        await message.reply_text("⏸ **Paused**", reply_markup=player(paused=True))
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


# ---------- /resume ----------
@Client.on_message(filters.command("resume", PREFIXES) & filters.group)
@require_assistant
async def resume_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in active_chats:
        return await message.reply_text("❌ Nothing to resume.")
    try:
        await safe_resume(chat_id)
        paused.discard(chat_id)
        await message.reply_text("▶️ **Resumed**", reply_markup=player(paused=False))
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


# ---------- /stop ----------
@Client.on_message(filters.command("stop", PREFIXES) & filters.group)
@require_assistant
async def stop_cmd(client, message: Message):
    chat_id = message.chat.id
    try:
        await safe_leave(chat_id)
    except Exception:
        pass
    clear_chat(chat_id)
    await message.reply_text("⏹ **Stopped & left voice chat.**")


# ---------- /skip ----------
@Client.on_message(filters.command(["skip", "next"], PREFIXES) & filters.group)
@require_assistant
async def skip_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in active_chats:
        return await message.reply_text("❌ Nothing is playing.")
    nxt = await play_next(chat_id)
    if nxt:
        await message.reply_text(
            now_playing(nxt),
            reply_markup=player(paused=False),
            disable_web_page_preview=True,
        )
    else:
        await message.reply_text("📭 Queue empty — stopped.")


# ---------- /seek ----------
@Client.on_message(filters.command("seek", PREFIXES) & filters.group)
@require_assistant
async def seek_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/seek 1:30`")
    secs = parse_timestamp(message.command[1])
    if secs < 0:
        return await message.reply_text("❌ Invalid time. Use `1:30` or `90`.")
    chat_id = message.chat.id
    cur = active_chats.get(chat_id)
    if not cur:
        return await message.reply_text("❌ Nothing playing.")
    try:
        try:
            await call_py.seek_stream(chat_id, secs)
        except AttributeError:
            await call_py.seek(chat_id, secs)
        await message.reply_text(f"⏩ **Seeked to** `{message.command[1]}`")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


# ---------- /volume ----------
@Client.on_message(filters.command("volume", PREFIXES) & filters.group)
@require_assistant
async def volume_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/volume 1-200`")
    try:
        vol = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Number daalo (1-200).")
    vol = max(1, min(200, vol))
    chat_id = message.chat.id
    if chat_id not in active_chats:
        return await message.reply_text("❌ Nothing playing.")
    try:
        # py-tgcalls volume change (if supported)
        if hasattr(call_py, "change_volume_call"):
            await call_py.change_volume_call(chat_id, vol)
        await message.reply_text(f"🔊 **Volume:** `{vol}%`")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")
