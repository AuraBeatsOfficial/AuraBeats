"""AuraBeats - /song /video media downloader."""
import os
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, FEATURE_DOWNLOADS
from utils.decorators import rate_limit
from utils.formatters import humanize_bytes, humanize_duration
from utils.logger import get_logger

log = get_logger("AuraBeats.Download")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

_AUDIO_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "default_search": "ytsearch1",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}

_VIDEO_OPTS = {
    "format": "best[ext=mp4][height<=720]/best[ext=mp4]/best",
    "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "default_search": "ytsearch1",
}


def _download(query: str, is_video: bool) -> dict:
    opts = _VIDEO_OPTS if is_video else _AUDIO_OPTS
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if "entries" in info:
            info = info["entries"][0]
        path = ydl.prepare_filename(info)
        if not is_video:
            path = os.path.splitext(path)[0] + ".mp3"
        return {
            "path":     path,
            "title":    info.get("title", "Unknown"),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", "—"),
            "thumb":    info.get("thumbnail"),
        }


async def _handle(client, message: Message, is_video: bool):
    if not FEATURE_DOWNLOADS:
        return await message.reply_text("⚠️ Downloads disabled.")
    if len(message.command) < 2:
        return await message.reply_text(f"Usage: `/{message.command[0]} <song name>`")

    query = " ".join(message.command[1:])
    status = await message.reply_text(
        f"📥 **Downloading {'video' if is_video else 'audio'}...**\n`{query}`"
    )

    try:
        data = await asyncio.to_thread(_download, query, is_video)
    except Exception as e:
        log.exception(f"download failed: {e}")
        return await status.edit_text(f"❌ **Download failed:**\n`{e}`")

    path = data["path"]
    if not os.path.exists(path):
        return await status.edit_text("❌ File not found after download.")

    size = humanize_bytes(os.path.getsize(path))
    dur = humanize_duration(data["duration"])

    await status.edit_text(
        f"📤 **Uploading...**\n\n**{data['title']}**\n"
        f"⏱ `{dur}` · 📦 `{size}`"
    )

    try:
        if is_video:
            await message.reply_video(
                video=path,
                caption=f"🎬 **{data['title']}**\n⏱ `{dur}` · 📦 `{size}`",
                duration=data["duration"],
                supports_streaming=True,
            )
        else:
            await message.reply_audio(
                audio=path,
                caption=f"🎵 **{data['title']}**\n⏱ `{dur}` · 📦 `{size}`",
                duration=data["duration"],
                performer=data["uploader"],
            )
        await status.delete()
    except Exception as e:
        log.exception(f"upload failed: {e}")
        await status.edit_text(f"❌ Upload failed: `{e}`")
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


@Client.on_message(filters.command("song", PREFIXES))
@rate_limit(5)
async def song_cmd(client, message: Message):
    await _handle(client, message, is_video=False)


@Client.on_message(filters.command("video", PREFIXES))
@rate_limit(5)
async def video_cmd(client, message: Message):
    await _handle(client, message, is_video=True)
