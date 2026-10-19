"""AuraBeats - yt-dlp wrapper (search + extract)."""
import asyncio
import yt_dlp
from utils.errors import SearchFailed
from utils.logger import get_logger

log = get_logger("AuraBeats.YT")

_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "skip_download": True,
    "nocheckcertificate": True,
    "default_search": "ytsearch1",
    "extract_flat": False,
    "source_address": "0.0.0.0",
    "geo_bypass": True,
    "noprogress": True,
}


def _extract(query: str) -> dict:
    with yt_dlp.YoutubeDL(_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
        if not info:
            raise SearchFailed("no result")
        if "entries" in info:
            entries = [e for e in info["entries"] if e]
            if not entries:
                raise SearchFailed("no entries")
            info = entries[0]
        # prefer m4a audio stream if available, else url
        url = info.get("url")
        if not url:
            for f in info.get("formats", []):
                if f.get("acodec") != "none" and f.get("vcodec") == "none":
                    url = f["url"]; break
        if not url:
            raise SearchFailed("no audio url")
        return {
            "id":         info.get("id"),
            "title":      info.get("title", "Unknown"),
            "url":        url,
            "webpage":    info.get("webpage_url"),
            "duration":   info.get("duration", 0),
            "thumbnail":  info.get("thumbnail"),
            "uploader":   info.get("uploader"),
            "views":      info.get("view_count", 0),
            "is_live":    info.get("is_live", False),
        }


async def search(query: str) -> dict:
    """Search YouTube (or a URL) and return track metadata."""
    log.info(f"Searching: {query[:60]}")
    try:
        return await asyncio.to_thread(_extract, query)
    except Exception as e:
        log.warning(f"search failed: {e}")
        raise SearchFailed(str(e)) from e


def _download_info(query: str) -> dict:
    with yt_dlp.YoutubeDL(_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info


async def get_formats(query: str) -> dict:
    """Return raw info dict (for /song, /video)."""
    try:
        return await asyncio.to_thread(_download_info, query)
    except Exception as e:
        raise SearchFailed(str(e)) from e
