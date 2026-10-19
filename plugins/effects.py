"""AuraBeats - /eq DSP audio effects."""
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, FEATURE_EFFECTS
from core.calls import call_py, active_chats
from utils.decorators import require_assistant
from utils.ffmpeg import list_presets, get_filter, pitch_shift, speed_change
from utils.streamer import build_audio
from utils.keyboard import eq_menu, player
from utils.logger import get_logger

log = get_logger("AuraBeats.Effects")


@Client.on_message(filters.command("eq", PREFIXES) & filters.group)
@require_assistant
async def eq_cmd(client, message: Message):
    if not FEATURE_EFFECTS:
        return await message.reply_text("⚠️ Effects disabled.")

    chat_id = message.chat.id

    if len(message.command) < 2:
        return await message.reply_text(
            "🎚 **Audio Effects**\n\n"
            f"**Presets:** `{'` · `'.join(list_presets())}`\n\n"
            "**Usage:** `/eq <preset>`\n"
            "**Pitch:** `/pitch <semitone -12..+12>`\n"
            "**Speed:** `/speed <0.5..2.0>`",
            reply_markup=eq_menu(),
        )

    preset = message.command[1].lower()
    if preset not in list_presets():
        return await message.reply_text(
            f"❌ Unknown preset.\n\nAvailable: `{'`, `'.join(list_presets())}`"
        )

    cur = active_chats.get(chat_id)
    if not cur:
        return await message.reply_text("❌ Play a song first to apply effects.")

    try:
        await call_py.play(chat_id, build_audio(cur["url"], preset=preset))
        await message.reply_text(
            f"🎚 **Effect applied:** `{preset}`\n\n"
            f"_Streaming `{cur['title'][:40]}` with {preset}._",
            reply_markup=player(paused=False),
        )
    except Exception as e:
        log.exception(f"eq apply failed: {e}")
        await message.reply_text(f"❌ `{e}`")


@Client.on_message(filters.command("pitch", PREFIXES) & filters.group)
@require_assistant
async def pitch_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/pitch <-12..12>`")
    try:
        n = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Number daalo.")
    n = max(-12, min(12, n))
    cur = active_chats.get(message.chat.id)
    if not cur:
        return await message.reply_text("❌ Nothing playing.")
    try:
        from pytgcalls.types import MediaStream, AudioQuality
        stream = MediaStream(
            cur["url"],
            audio_parameters=AudioQuality.HIGH,
            ffmpeg_parameters=f"-af \"{pitch_shift(n)}\"",
        )
        await call_py.play(message.chat.id, stream)
        await message.reply_text(f"🎵 **Pitch:** `{n:+d}` semitones")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


@Client.on_message(filters.command("speed", PREFIXES) & filters.group)
@require_assistant
async def speed_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/speed <0.5..2.0>`")
    try:
        f = float(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Number daalo (0.5-2.0).")
    f = max(0.5, min(2.0, f))
    cur = active_chats.get(message.chat.id)
    if not cur:
        return await message.reply_text("❌ Nothing playing.")
    try:
        from pytgcalls.types import MediaStream, AudioQuality
        stream = MediaStream(
            cur["url"],
            audio_parameters=AudioQuality.HIGH,
            ffmpeg_parameters=f"-af \"{speed_change(f)}\"",
        )
        await call_py.play(message.chat.id, stream)
        await message.reply_text(f"⏩ **Speed:** `{f:.2f}x`")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")
