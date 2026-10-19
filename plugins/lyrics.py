"""AuraBeats - /lyrics (via lyrics.ovh free API)."""
import aiohttp
import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, FEATURE_LYRICS
from utils.yt_helper import search
from utils.formatters import truncate
from utils.logger import get_logger

log = get_logger("AuraBeats.Lyrics")

_LYRICS_API = "https://api.lyrics.ovh/v1/{artist}/{title}"
_MAX_LEN = 3800


async def _fetch_lyrics(artist: str, title: str) -> str | None:
    url = _LYRICS_API.format(
        artist=urllib.parse.quote(artist),
        title=urllib.parse.quote(title),
    )
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as s:
            async with s.get(url) as r:
                if r.status != 200:
                    return None
                data = await r.json()
                return data.get("lyrics")
    except Exception as e:
        log.warning(f"lyrics fetch failed: {e}")
        return None


@Client.on_message(filters.command("lyrics", PREFIXES))
async def lyrics_cmd(client, message: Message):
    if not FEATURE_LYRICS:
        return await message.reply_text("⚠️ Lyrics module disabled.")

    query = " ".join(message.command[1:]).strip() if len(message.command) > 1 else ""
    if not query:
        return await message.reply_text(
            "Usage: `/lyrics <song name>`\n"
            "Or reply to a song with `/lyrics`"
        )

    status = await message.reply_text(f"🎤 **Finding lyrics for** `{truncate(query, 40)}`…")

    # Search to get real title + uploader
    try:
        info = await search(query)
    except Exception as e:
        return await status.edit_text(f"❌ `{e}`")

    title = info.get("title", query)
    uploader = info.get("uploader", "")

    # clean title (remove common suffixes)
    clean_title = title
    for junk in ("(Official Video)", "(Lyrics)", "(Audio)", "|", "[", "]",
                 "(Official)", "(Music Video)", "ft.", "Ft."):
        clean_title = clean_title.split(junk)[0]
    clean_title = clean_title.strip()

    clean_artist = uploader.split(" - ")[0].replace("VEVO", "").strip()

    lyrics = await _fetch_lyrics(clean_artist, clean_title)
    if not lyrics:
        # fallback: try with just title
        lyrics = await _fetch_lyrics("", clean_title)

    if not lyrics:
        return await status.edit_text(
            f"❌ **Lyrics not found** for:\n`{clean_title}`\n\n"
            f"Try exact song name or artist name."
        )

    lyrics = lyrics.strip()
    header = f"🎤 **{clean_title}**\n"
    if clean_artist:
        header += f"🎙 _{clean_artist}_\n\n"

    body = lyrics[:_MAX_LEN]
    if len(lyrics) > _MAX_LEN:
        body += "\n\n_…lyrics truncated (too long)_"

    await status.edit_text(header + body, disable_web_page_preview=True)
